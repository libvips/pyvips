# vim: set fileencoding=utf-8 :

import struct
import sys

import pyvips
import pytest
from helpers import JPEG_FILE, UHDR_FILE, skip_if_no


class TestImage:
    def test_pagejoin(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        many_page = image.pagejoin([image, image])
        assert many_page.get_page_height() == image.height
        assert many_page.height / many_page.get_page_height() == 3

    def test_pagesplit(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        many_page = image.pagejoin([image, image])
        image_list = many_page.pagesplit()
        assert len(image_list) == 3

    def test_bandjoin(self):
        black = pyvips.Image.black(16, 16)
        a = black.draw_rect(1, 0, 0, 1, 1)
        b = black.draw_rect(2, 0, 0, 1, 1)
        c = black.draw_rect(3, 0, 0, 1, 1)
        im = a.bandjoin([b, c, a, b, c, a, b, c])

        assert im.width == 16
        assert im.height == 16
        assert im.bands == 9

        x = im.bandjoin([])
        assert x.bands == 9

    def test_bandslice(self):
        black = pyvips.Image.black(16, 16)
        a = black.draw_rect(1, 0, 0, 1, 1)
        b = black.draw_rect(2, 0, 0, 1, 1)
        c = black.draw_rect(3, 0, 0, 1, 1)
        d = black.draw_rect(4, 0, 0, 1, 1)
        e = black.draw_rect(5, 0, 0, 1, 1)
        f = black.draw_rect(6, 0, 0, 1, 1)

        im = black.bandjoin([a, b, c, d, e, f])

        seq = list(range(im.bands))

        x = im[1]

        assert x.bands == 1
        assert x(0, 0) == [seq[1]]

        x = im[1:4]

        assert x.bands == 3
        assert x(0, 0) == seq[1:4]

        x = im[1:4][::-1]

        assert x.bands == 3
        assert x(0, 0) == seq[1:4][::-1]

        x = im[-7]
        assert x(0, 0) == [seq[-7]]

        x = im[::-1]

        assert x(0, 0) == seq[::-1]

        x = im[4:6]

        assert x(0, 0) == seq[4:6]

        x = im[5:3:-1]

        assert x(0, 0) == seq[5:3:-1]

        x = im[2:4:2]

        assert x(0, 0) == seq[2:4:2]

        c = im[2:0:-2]

        assert x(0, 0) == seq[2:0:-2]

        x = im[::-2]

        assert x(0, 0) == seq[::-2]

        x = im[1::-2]

        assert x(0, 0) == seq[1::-2]

        x = im[:5:-2]

        assert x(0, 0) == seq[:5:-2]

        x = im[5:0:-2]

        assert x(0, 0) == seq[5:0:-2]

        x = im[-10:10]

        assert x(0, 0) == seq[-10:10]

        indices = [1, 2, 5]
        x = im[indices]

        assert x(0, 0) == [seq[i] for i in indices]

        indices = [1, 2, -7]
        x = im[indices]

        assert x(0, 0) == [seq[i] for i in indices]

        indices = [1]
        x = im[indices]

        assert x(0, 0) == [seq[1]]

        indices = [-1]
        x = im[indices]

        assert x(0, 0) == [seq[-1]]

        boolslice = [True, True, False, False, True, True, False]
        x = im[boolslice]
        assert x(0, 0) == [seq[i] for i, b in enumerate(boolslice) if b]

        with pytest.raises(IndexError):
            x = im[4:1]

        with pytest.raises(IndexError):
            x = im[-(im.bands + 1)]

        with pytest.raises(IndexError):
            x = im[im.bands]

        with pytest.raises(IndexError):
            empty = [False] * im.bands
            x = im[empty]

        with pytest.raises(IndexError):
            notenough = [True] * (im.bands - 1)
            x = im[notenough]

        with pytest.raises(IndexError):
            toomany = [True] * (im.bands + 1)
            x = im[toomany]

        with pytest.raises(IndexError):
            empty = []
            x = im[empty]

        with pytest.raises(IndexError):
            oob = [2, 3, -8]
            x = im[oob]

        with pytest.raises(IndexError):
            mixed = [True, 1, True, 2, True, 3, True]
            x = im[mixed]

        with pytest.raises(IndexError):
            wrongtypelist = ['a', 'b', 'c']
            x = im[wrongtypelist]

        with pytest.raises(IndexError):
            wrongargtype = dict(a=1, b=2)
            x = im[wrongargtype]

    def test_invalidate(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip('numpy not available')

        a = np.zeros((1, 1))
        p = pyvips.Image.new_from_memory(a.data, 1, 1, 1, 'double')
        v = p(0, 0)
        assert v == [0]
        a[0, 0] = 1
        v = p(0, 0)
        assert v == [0]
        p.invalidate()
        v = p(0, 0)
        assert v == [1]

    def test_to_numpy(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip('numpy not available')

        xy = pyvips.Image.xyz(4, 5)

        # using __array__ interface:

        from pyvips.vimage import TYPESTR_TO_FORMAT
        for typestr, format in TYPESTR_TO_FORMAT.items():
            this_xy = xy.cast(format)
            if typestr == '|b1':
                yx = np.asarray(this_xy, dtype=typestr)
            else:
                yx = np.array(this_xy)

            assert yx.dtype == np.dtype(typestr)
            assert yx.shape == (5, 4, 2)
            assert all(yx.max(axis=(0, 1)) == np.array([3, 4], dtype=typestr))

        x, y = xy
        x_iy = pyvips.Image.complexform(x, y)
        x_iy_dp = x_iy.cast('dpcomplex')

        a = np.array(x_iy)
        assert a.shape == (5, 4)
        assert a.dtype == np.dtype('complex64')
        assert a[4, 3].item() == 3+4j

        a = np.array(x_iy_dp)
        assert a.shape == (5, 4)
        assert a.dtype == np.dtype('complex128')
        assert a[4, 3].item() == 3+4j

        xyxyxy = xy.bandjoin([xy, xy])
        a = np.array(xyxyxy)
        assert a.shape == (5, 4, 6)

        # axes collapsing:
        xyxyxy_col = xyxyxy.crop(3, 0, 1, 5)
        assert xyxyxy_col.width == 1
        assert xyxyxy_col.height == 5
        a = np.array(xyxyxy_col)
        assert a.shape == (5, 1, 6)

        xyxyxy_row = xyxyxy.crop(0, 4, 4, 1)
        assert xyxyxy_row.width == 4
        assert xyxyxy_row.height == 1
        a = np.array(xyxyxy_row)
        assert a.shape == (1, 4, 6)

        xyxyxy_px = xyxyxy.crop(3, 4, 1, 1)
        assert xyxyxy_px.width == 1
        assert xyxyxy_px.height == 1
        a = np.array(xyxyxy_px)
        assert a.shape == (1, 1, 6)

        a = np.array(xyxyxy_px[0])
        assert a.ndim == 0

        # automatic conversion to array on ufunc application:

        d = np.diff(xy.cast('short'), axis=1)
        assert (d[..., 0] == 1).all()
        assert (d[..., 1] == 0).all()

        # tests of .numpy() method:

        a = pyvips.Image.xyz(256, 1)[0].numpy().squeeze()

        assert all(a == np.arange(256))

    def test_scipy(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip('numpy not available')

        try:
            from scipy import ndimage
        except ImportError:
            pytest.skip('scipy not available')

        black = pyvips.Image.black(16, 16)
        a = black.draw_rect(1, 0, 0, 1, 1)

        d = ndimage.distance_transform_edt(a == 0)
        assert np.allclose(d[-1, -1], (2 * 15 ** 2) ** 0.5)

    def test_torch(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip('numpy not available')

        try:
            import torch
        except ImportError:
            pytest.skip('torch not available')

        # torch to Image:
        x = torch.outer(torch.arange(10), torch.arange(5))
        with pytest.raises(ValueError):
            # no vips format for int64
            im = pyvips.Image.new_from_array(x)

        x = x.float()

        im = pyvips.Image.new_from_array(x)
        assert im.width == 5
        assert im.height == 10
        assert im(4, 9) == [36]
        assert im.format == 'float'

        # Image to torch:
        im = pyvips.Image.zone(5, 5)
        t = torch.from_numpy(np.asarray(im))
        assert t[2, 2] == 1.

    def test_from_numpy(self):
        try:
            import numpy as np
        except ImportError:
            pytest.skip('numpy not available')

        a = np.indices((5, 4)).transpose(1, 2, 0)  # (5, 4, 2)

        with pytest.raises(ValueError):
            # no way in for int64
            yx = pyvips.Image.new_from_array(a)

        from pyvips.vimage import TYPESTR_TO_FORMAT

        for typestr, format in TYPESTR_TO_FORMAT.items():
            if typestr == '|b1':
                continue
            a = np.indices((5, 4), dtype=typestr).transpose(1, 2, 0)
            yx = pyvips.Image.new_from_array(a)
            assert yx.format == format

        a = np.zeros((2, 2, 2, 2))

        with pytest.raises(ValueError):
            # too many dimensions
            im = pyvips.Image.new_from_array(a)

        a = np.ones((2, 2, 2), dtype=bool)
        im = pyvips.Image.new_from_array(a)
        assert im.max() == 255

        a = np.ones((2, 2, 2), dtype='S8')
        with pytest.raises(ValueError):
            # no way in for strings
            im = pyvips.Image.new_from_array(a)

        # test handling of strided data
        a = np.ones((1000, 1000, 3), dtype='uint8')[::10, ::10]
        im = pyvips.Image.new_from_array(a)
        assert im.width == 100
        assert im.height == 100
        assert im.bands == 3

        class FakeArray(object):
            @property
            def __array_interface__(self):
                return {'shape': (1, 1, 1),
                        'typestr': '|u1',
                        'version': 3}

        with pytest.raises(TypeError):
            # Handle evil objects that don't behave like ndarrays
            im = pyvips.Image.new_from_array(FakeArray())

    def test_tolist(self):
        im = pyvips.Image.complexform(*pyvips.Image.xyz(3, 4))

        assert im.tolist()[-1][-1] == 2+3j

        im = im.cast('dpcomplex')

        assert im.tolist()[-1][-1] == 2+3j

        lst = [[1, 2, 3], [4, 5, 6]]

        im = pyvips.Image.new_from_array(lst)

        assert im.tolist() == lst

        assert im.cast('float').tolist() == lst
        assert im.cast('complex').tolist() == lst

    def test_from_PIL(self):
        try:
            import PIL.Image
        except ImportError:
            pytest.skip('PIL not available')

        pim = PIL.Image.new('RGB', (42, 23))

        im = pyvips.Image.new_from_array(pim)
        assert im.format == 'uchar'
        assert im.interpretation == 'srgb'
        assert im.width == pim.width
        assert im.height == pim.height
        assert im.min() == 0
        assert im.max() == 0

    def test_to_PIL_16bit(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        endian = '<' if sys.byteorder == 'little' else '>'
        data = struct.pack(
            f'{endian}6H',
            0x1234,
            0x5678,
            0x9ABC,
            0xDEF0,
            0x1111,
            0x2222
        )
        im = pyvips.Image.new_from_memory(data, 2, 1, 3, 'ushort')

        pim = im.pil()
        assert pim.mode == 'RGB'
        assert pim.size == (2, 1)
        assert pim.getpixel((0, 0)) == (0x12, 0x56, 0x9A)
        assert pim.getpixel((1, 0)) == (0xDE, 0x11, 0x22)

    def test_to_PIL_16bit_rawmode_rgb_rgba(self, monkeypatch):
        try:
            import PIL.Image as PILImage
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        seen = []

        def fake_frombytes(mode, size, data, decoder_name, rawmode):
            seen.append((mode, rawmode))
            return PILImage.new(mode, size)

        monkeypatch.setattr(PILImage, "frombytes", fake_frombytes)

        data = struct.pack('6H', 0x1234, 0x5678, 0x9ABC, 0xDEF0,
                           0x1111, 0x2222)
        im = pyvips.Image.new_from_memory(data, 2, 1, 3, 'ushort')
        im.pil()

        data = struct.pack('8H', 0x1234, 0x5678, 0x9ABC, 0xDEF0,
                           0x1111, 0x2222, 0x3333, 0x4444)
        im = pyvips.Image.new_from_memory(data, 2, 1, 4, 'ushort')
        im.pil()

        assert seen[0][0] == 'RGB'
        assert seen[1][0] == 'RGBA'
        assert seen[0][1] in ('RGB;16L', 'RGB;16B')
        assert seen[1][1] in ('RGBA;16L', 'RGBA;16B')

    def test_to_PIL_8bit_modes(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        im = pyvips.Image.new_from_memory(bytes([0, 128, 255, 64]),
                                          2, 2, 1, 'uchar')
        pim = im.pil()
        assert pim.mode == 'L'
        assert pim.size == (2, 2)
        assert pim.getpixel((0, 0)) == 0
        assert pim.getpixel((1, 0)) == 128

        im = pyvips.Image.new_from_memory(bytes([10, 20, 30, 40]),
                                          2, 1, 2, 'uchar')
        pim = im.pil()
        assert pim.mode == 'LA'
        assert pim.getpixel((0, 0)) == (10, 20)
        assert pim.getpixel((1, 0)) == (30, 40)

        im = pyvips.Image.new_from_memory(bytes([1, 2, 3, 4, 5, 6]),
                                          2, 1, 3, 'uchar')
        pim = im.pil()
        assert pim.mode == 'RGB'
        assert pim.getpixel((0, 0)) == (1, 2, 3)
        assert pim.getpixel((1, 0)) == (4, 5, 6)

        im = pyvips.Image.new_from_memory(bytes([1, 2, 3, 4, 5, 6, 7, 8]),
                                          2, 1, 4, 'uchar')
        pim = im.pil()
        assert pim.mode == 'RGBA'
        assert pim.getpixel((0, 0)) == (1, 2, 3, 4)
        assert pim.getpixel((1, 0)) == (5, 6, 7, 8)

    def test_to_PIL_16bit_la(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        endian = '<' if sys.byteorder == 'little' else '>'
        data = struct.pack(
            f'{endian}4H',
            0x1234,
            0x5678,
            0x9ABC,
            0xDEF0
        )
        im = pyvips.Image.new_from_memory(data, 2, 1, 2, 'ushort')

        pim = im.pil()
        assert pim.mode == 'RGBA'
        assert pim.size == (2, 1)
        assert pim.getpixel((0, 0)) == (0x12, 0x12, 0x12, 0x56)
        assert pim.getpixel((1, 0)) == (0x9A, 0x9A, 0x9A, 0xDE)

    def test_to_PIL_16bit_rgba(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        endian = '<' if sys.byteorder == 'little' else '>'
        data = struct.pack(
            f'{endian}8H',
            0x1234,
            0x5678,
            0x9ABC,
            0xDEF0,
            0x1111,
            0x2222,
            0x3333,
            0x4444
        )
        im = pyvips.Image.new_from_memory(data, 2, 1, 4, 'ushort')

        pim = im.pil()
        assert pim.mode == 'RGBA'
        assert pim.size == (2, 1)
        assert pim.getpixel((0, 0)) == (0x12, 0x56, 0x9A, 0xDE)
        assert pim.getpixel((1, 0)) == (0x11, 0x22, 0x33, 0x44)

    def test_to_PIL_16bit_l(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        endian = '<' if sys.byteorder == 'little' else '>'
        data = struct.pack(f'{endian}2H', 0x1234, 0x9ABC)
        im = pyvips.Image.new_from_memory(data, 2, 1, 1, 'ushort')

        pim = im.pil()
        assert pim.size == (2, 1)
        assert pim.getpixel((0, 0)) == 0x1234
        assert pim.getpixel((1, 0)) == 0x9ABC

    def test_to_PIL_16bit_5band_unsupported(self):
        try:
            import PIL.Image        # noqa: F401
        except ImportError:
            pytest.skip('PIL not available')

        try:
            import numpy as np      # noqa: F401
        except ImportError:
            pytest.skip('numpy not available')

        data = struct.pack('5H', 0x1111, 0x2222, 0x3333, 0x4444, 0x5555)
        im = pyvips.Image.new_from_memory(data, 1, 1, 5, 'ushort')

        with pytest.raises(ValueError):
            im.pil()

    @skip_if_no('uhdrload')
    def test_gainmap(self):
        def crop_gainmap(image):
            gainmap = image.get_gainmap()

            if gainmap:
                new_gainmap = gainmap.crop(0, 0, 10, 10)
                image = image.copy()
                image.set_type(pyvips.GValue.image_type,
                               "gainmap", new_gainmap)

            return image

        image = pyvips.Image.new_from_file(UHDR_FILE)
        image = crop_gainmap(image)
        buf = image.write_to_buffer(".jpg")
        new_image = pyvips.Image.new_from_buffer(buf, "")
        new_gainmap = new_image.get_gainmap()

        assert new_gainmap.width == 10
