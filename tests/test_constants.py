# vim: set fileencoding=utf-8 :

import pyvips


class TestConstants:
    def test_2Darray(self):
        im = pyvips.Image.new_from_array([[1, 2, 3, 4], [5, 6, 7, 8]])
        assert im.width == 4
        assert im.height == 2

    def test_1Darray(self):
        im = pyvips.Image.new_from_array([1, 2, 3, 4])
        assert im.width == 4
        assert im.height == 1

    def test_array_const_args(self):
        black = pyvips.Image.black(16, 16)
        r = black.draw_rect(255, 10, 12, 1, 1)
        g = black.draw_rect(255, 10, 11, 1, 1)
        b = black.draw_rect(255, 10, 10, 1, 1)
        im = r.bandjoin([g, b])

        assert im.width == 16
        assert im.height == 16
        assert im.bands == 3

        im = im.conv([
            [0.11, 0.11, 0.11],
            [0.11, 0.11, 0.11],
            [0.11, 0.11, 0.11]
        ])

        assert im.width == 16
        assert im.height == 16
        assert im.bands == 3

    def test_scale_offset(self):
        im = pyvips.Image.new_from_array([1, 2], 8, 2)

        assert im.width == 2
        assert im.height == 1
        assert im.bands == 1
        assert im.scale == 8
        assert im.offset == 2
        assert im.avg() == 1.5

    def test_binary_scalar(self):
        im = pyvips.Image.black(16, 16) + 128

        im += 128
        im -= 128
        im *= 2
        im /= 2
        im %= 100
        im += 100
        im **= 2
        im **= 0.5
        im <<= 1
        im >>= 1
        im |= 64
        im &= 32
        im ^= 128

        assert im.avg() == 128

    def test_binary_vector(self):
        im = pyvips.Image.black(16, 16, bands=3) + 128

        im += [128, 0, 0]
        im -= [128, 0, 0]
        im *= [2, 1, 1]
        im /= [2, 1, 1]
        im %= [100, 99, 98]
        im += [100, 99, 98]
        im **= [2, 3, 4]
        im **= [1.0 / 2.0, 1.0 / 3.0, 1.0 / 4.0]
        im <<= [1, 2, 3]
        im >>= [1, 2, 3]
        im |= [64, 128, 256]
        im &= [64, 128, 256]
        im ^= [64 + 128, 0, 256 + 128]

        assert im.avg() == 128

    def test_binary_image(self):
        im = pyvips.Image.black(16, 16) + 128
        x = im

        x += im
        x -= im
        x *= im
        x /= im
        x %= im
        x += im
        x |= im
        x &= im
        x ^= im

        assert x.avg() == 0

    def test_binary_relational_scalar(self):
        im = pyvips.Image.black(16, 16) + 128

        assert (im > 128).avg() == 0
        assert (im >= 128).avg() == 255
        assert (im < 128).avg() == 0
        assert (im <= 128).avg() == 255
        assert (im == 128).avg() == 255
        assert (im != 128).avg() == 0

    def test_binary_relational_vector(self):
        im = pyvips.Image.black(16, 16, bands=3) + [100, 128, 130]

        assert (im > [100, 128, 130]).avg() == 0
        assert (im >= [100, 128, 130]).avg() == 255
        assert (im < [100, 128, 130]).avg() == 0
        assert (im <= [100, 128, 130]).avg() == 255
        assert (im == [100, 128, 130]).avg() == 255
        assert (im != [100, 128, 130]).avg() == 0

    def test_binary_relational_image(self):
        im = pyvips.Image.black(16, 16) + 128

        assert (im > im).avg() == 0
        assert (im >= im).avg() == 255
        assert (im < im).avg() == 0
        assert (im <= im).avg() == 255
        assert (im == im).avg() == 255
        assert (im != im).avg() == 0

    def test_band_extract_scalar(self):
        im = pyvips.Image.black(16, 16, bands=3) + [100, 128, 130]
        x = im[1]

        assert x.width == 16
        assert x.height == 16
        assert x.bands == 1
        assert x.avg() == 128

    def test_band_extract_slice(self):
        im = pyvips.Image.black(16, 16, bands=3) + [100, 128, 130]
        x = im[1:3]

        assert x.width == 16
        assert x.height == 16
        assert x.bands == 2
        assert x.avg() == 129
