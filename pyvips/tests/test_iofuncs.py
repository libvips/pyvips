# vim: set fileencoding=utf-8 :
import unittest

import pyvips
from .helpers import PyvipsTester


class TestIofuncs(PyvipsTester):
    # test the vips7 filename splitter ... this is very fragile and annoying
    # code with lots of cases
    def test_split7(self):
        def split(path):
            filename7 = pyvips.path_filename7(path)
            mode7 = pyvips.path_mode7(path)

            return [filename7, mode7]

        cases = [
            ["c:\\silly:dir:name\\fr:ed.tif:jpeg:95,,,,c:\\icc\\srgb.icc",
             ["c:\\silly:dir:name\\fr:ed.tif",
              "jpeg:95,,,,c:\\icc\\srgb.icc"]],
            ["I180:",
             ["I180",
              ""]],
            ["c:\\silly:",
             ["c:\\silly",
              ""]],
            ["c:\\program files\\x:hello",
             ["c:\\program files\\x",
              "hello"]],
            ["C:\\fixtures\\2569067123_aca715a2ee_o.jpg",
             ["C:\\fixtures\\2569067123_aca715a2ee_o.jpg",
              ""]]
        ]

        for case in cases:
            self.assertEqualObjects(split(case[0]), case[1])

    def test_new_from_image(self):
        im = pyvips.Image.mask_ideal(100, 100, 0.5,
                                     reject=True, optical=True)

        im2 = im.new_from_image(12)

        self.assertEqual(im2.width, im.width)
        self.assertEqual(im2.height, im.height)
        self.assertEqual(im2.interpretation, im.interpretation)
        self.assertEqual(im2.format, im.format)
        self.assertEqual(im2.xres, im.xres)
        self.assertEqual(im2.yres, im.yres)
        self.assertEqual(im2.xoffset, im.xoffset)
        self.assertEqual(im2.yoffset, im.yoffset)
        self.assertEqual(im2.bands, 1)
        self.assertEqual(im2.avg(), 12)

        im2 = im.new_from_image([1, 2, 3])

        self.assertEqual(im2.bands, 3)
        self.assertEqual(im2.avg(), 2)

    def test_new_from_memory(self):
        s = bytearray(200)
        im = pyvips.Image.new_from_memory(s, 20, 10, 1, 'uchar')

        self.assertEqual(im.width, 20)
        self.assertEqual(im.height, 10)
        self.assertEqual(im.format, 'uchar')
        self.assertEqual(im.bands, 1)
        self.assertEqual(im.avg(), 0)

        im += 10

        self.assertEqual(im.avg(), 10)

    def test_get_fields(self):
        im = pyvips.Image.mask_ideal(100, 100, 0.5,
                                     reject=True, optical=True)
        fields = im.get_fields()
        # we might add more fields later
        self.assertTrue(len(fields) > 10)
        self.assertEqual(fields[0], 'width')

    def test_write_to_memory(self):
        s = bytearray(200)
        im = pyvips.Image.new_from_memory(s, 20, 10, 1, 'uchar')
        t = im.write_to_memory()

        self.assertEqual(s, t)


if __name__ == '__main__':
    unittest.main()
