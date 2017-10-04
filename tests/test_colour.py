# vim: set fileencoding=utf-8 :
import unittest

import pyvips
from .helpers import PyvipsTester, JPEG_FILE, SRGB_FILE, \
    colour_colourspaces, mono_colourspaces


class TestColour(PyvipsTester):
    def setUp(self):
        im = pyvips.Image.mask_ideal(100, 100, 0.5,
                                     reject=True, optical=True)
        self.colour = im * [1, 2, 3] + [2, 3, 4]
        self.mono = self.colour.extract_band(1)
        self.all_images = [self.mono, self.colour]

    def test_colourspace(self):
        # mid-grey in Lab ... put 42 in the extra band, it should be copied
        # unmodified
        test = pyvips.Image.black(100, 100) + [50, 0, 0, 42]
        test = test.copy(interpretation=pyvips.Interpretation.LAB)

        # a long series should come in a circle
        im = test
        for col in colour_colourspaces + [pyvips.Interpretation.LAB]:
            im = im.colourspace(col)
            self.assertEqual(im.interpretation, col)

            for i in range(0, 4):
                min_l = im.extract_band(i).min()
                max_h = im.extract_band(i).max()
                self.assertAlmostEqual(min_l, max_h)

            pixel = im(10, 10)
            self.assertAlmostEqual(pixel[3], 42, places=2)

        # alpha won't be equal for RGB16, but it should be preserved if we go
        # there and back
        im = im.colourspace(pyvips.Interpretation.RGB16)
        im = im.colourspace(pyvips.Interpretation.LAB)

        before = test(10, 10)
        after = im(10, 10)
        self.assertAlmostEqualObjects(before, after, places=1)

        # go between every pair of colour spaces
        for start in colour_colourspaces:
            for end in colour_colourspaces:
                im = test.colourspace(start)
                im2 = im.colourspace(end)
                im3 = im2.colourspace(pyvips.Interpretation.LAB)

                before = test(10, 10)
                after = im3(10, 10)

                self.assertAlmostEqualObjects(before, after, places=1)

        # test Lab->XYZ on mid-grey
        # checked against http://www.brucelindbloom.com
        im = test.colourspace(pyvips.Interpretation.XYZ)
        after = im(10, 10)
        self.assertAlmostEqualObjects(after, [17.5064, 18.4187, 20.0547, 42])

        # grey->colour->grey should be equal
        for mono_fmt in mono_colourspaces:
            test_grey = test.colourspace(mono_fmt)
            im = test_grey
            for col in colour_colourspaces + [mono_fmt]:
                im = im.colourspace(col)
                self.assertEqual(im.interpretation, col)
            [before, alpha_before] = test_grey(10, 10)
            [after, alpha_after] = im(10, 10)
            self.assertLess(abs(alpha_after - alpha_before), 1)
            if mono_fmt == pyvips.Interpretation.GREY16:
                # GREY16 can wind up rather different due to rounding
                self.assertLess(abs(after - before), 30)
            else:
                # but 8-bit we should hit exactly
                self.assertLess(abs(after - before), 1)

    # test results from Bruce Lindbloom's calculator:
    # http://www.brucelindbloom.com

    def test_dE00(self):
        # put 42 in the extra band, it should be copied unmodified
        reference = pyvips.Image.black(100, 100) + [50, 10, 20, 42]
        reference = reference.copy(interpretation=pyvips.Interpretation.LAB)
        sample = pyvips.Image.black(100, 100) + [40, -20, 10]
        sample = sample.copy(interpretation=pyvips.Interpretation.LAB)

        difference = reference.dE00(sample)
        result, alpha = difference(10, 10)
        self.assertAlmostEqual(result, 30.238, places=3)
        self.assertAlmostEqual(alpha, 42.0, places=3)

    def test_dE76(self):
        # put 42 in the extra band, it should be copied unmodified
        reference = pyvips.Image.black(100, 100) + [50, 10, 20, 42]
        reference = reference.copy(interpretation=pyvips.Interpretation.LAB)
        sample = pyvips.Image.black(100, 100) + [40, -20, 10]
        sample = sample.copy(interpretation=pyvips.Interpretation.LAB)

        difference = reference.dE76(sample)
        result, alpha = difference(10, 10)
        self.assertAlmostEqual(result, 33.166, places=3)
        self.assertAlmostEqual(alpha, 42.0, places=3)

    # the vips CMC calculation is based on distance in a colorspace
    # derived from the CMC formula, so it won't match exactly ...
    # see vips_LCh2CMC() for details
    def test_dECMC(self):
        reference = pyvips.Image.black(100, 100) + [50, 10, 20, 42]
        reference = reference.copy(interpretation=pyvips.Interpretation.LAB)
        sample = pyvips.Image.black(100, 100) + [55, 11, 23]
        sample = sample.copy(interpretation=pyvips.Interpretation.LAB)

        difference = reference.dECMC(sample)
        result, alpha = difference(10, 10)
        self.assertLess(abs(result - 4.97), 0.5)
        self.assertAlmostEqual(alpha, 42.0, places=3)

    def test_icc(self):
        test = pyvips.Image.new_from_file(JPEG_FILE)

        im = test.icc_import().icc_export()
        self.assertLess(im.dE76(test).max(), 6)

        im = test.icc_import()
        im2 = im.icc_export(depth=16)
        self.assertEqual(im2.format, pyvips.BandFormat.USHORT)
        im3 = im2.icc_import()
        self.assertLess((im - im3).abs().max(), 3)

        im = test.icc_import(intent=pyvips.Intent.ABSOLUTE)
        im2 = im.icc_export(intent=pyvips.Intent.ABSOLUTE)
        self.assertLess(im2.dE76(test).max(), 6)

        im = test.icc_import()
        im2 = im.icc_export(output_profile=SRGB_FILE)
        im3 = im.colourspace(pyvips.Interpretation.SRGB)
        self.assertLess(im2.dE76(im3).max(), 6)

        before_profile = test.get_value("icc-profile-data")
        im = test.icc_transform(SRGB_FILE)
        after_profile = im.get_value("icc-profile-data")
        im2 = test.icc_import()
        im3 = im2.colourspace(pyvips.Interpretation.SRGB)
        self.assertLess(im.dE76(im3).max(), 6)
        self.assertNotEqual(len(before_profile), len(after_profile))

        im = test.icc_import(input_profile=SRGB_FILE)
        im2 = test.icc_import()
        self.assertLess(6, im.dE76(im2).max())

        im = test.icc_import(pcs=pyvips.PCS.XYZ)
        self.assertEqual(im.interpretation, pyvips.Interpretation.XYZ)
        im = test.icc_import()
        self.assertEqual(im.interpretation, pyvips.Interpretation.LAB)


if __name__ == '__main__':
    unittest.main()
