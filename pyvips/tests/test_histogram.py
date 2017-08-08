# vim: set fileencoding=utf-8 :
import unittest

import pyvips
from .helpers import PyvipsTester, JPEG_FILE


class TestHistogram(PyvipsTester):
    def test_hist_cum(self):
        im = pyvips.Image.identity()

        sum = im.avg() * 256

        cum = im.hist_cum()

        p = cum(255, 0)
        self.assertEqual(p[0], sum)

    def test_hist_equal(self):
        im = pyvips.Image.new_from_file(JPEG_FILE)

        im2 = im.hist_equal()

        self.assertEqual(im.width, im2.width)
        self.assertEqual(im.height, im2.height)

        self.assertTrue(im.avg() < im2.avg())
        self.assertTrue(im.deviate() < im2.deviate())

    def test_hist_ismonotonic(self):
        im = pyvips.Image.identity()
        self.assertTrue(im.hist_ismonotonic())

    def test_hist_local(self):
        im = pyvips.Image.new_from_file(JPEG_FILE)

        im2 = im.hist_local(10, 10)

        self.assertEqual(im.width, im2.width)
        self.assertEqual(im.height, im2.height)

        self.assertTrue(im.avg() < im2.avg())
        self.assertTrue(im.deviate() < im2.deviate())

        im3 = im.hist_local(10, 10, max_slope=3)

        self.assertEqual(im.width, im2.width)
        self.assertEqual(im.height, im2.height)

        self.assertTrue(im3.deviate() < im2.deviate())

    def test_hist_match(self):
        im = pyvips.Image.identity()
        im2 = pyvips.Image.identity()

        matched = im.hist_match(im2)

        self.assertEqual((im - matched).abs().max(), 0.0)

    def test_hist_norm(self):
        im = pyvips.Image.identity()
        im2 = im.hist_norm()

        self.assertEqual((im - im2).abs().max(), 0.0)

    def test_hist_plot(self):
        im = pyvips.Image.identity()
        im2 = im.hist_plot()

        self.assertEqual(im2.width, 256)
        self.assertEqual(im2.height, 256)
        self.assertEqual(im2.format, pyvips.BandFormat.UCHAR)
        self.assertEqual(im2.bands, 1)

    def test_hist_map(self):
        im = pyvips.Image.identity()

        im2 = im.maplut(im)

        self.assertEqual((im - im2).abs().max(), 0.0)

    def test_percent(self):
        im = pyvips.Image.new_from_file(JPEG_FILE).extract_band(1)

        pc = im.percent(90)

        msk = im <= pc
        n_set = (msk.avg() * msk.width * msk.height) / 255.0
        pc_set = 100 * n_set / (msk.width * msk.height)

        self.assertAlmostEqual(pc_set, 90, places=0)

    def test_hist_entropy(self):
        im = pyvips.Image.new_from_file(JPEG_FILE).extract_band(1)

        ent = im.hist_find().hist_entropy()

        self.assertAlmostEqual(ent, 4.37, places=2)

    def test_stdif(self):
        im = pyvips.Image.new_from_file(JPEG_FILE)

        im2 = im.stdif(10, 10)

        self.assertEqual(im.width, im2.width)
        self.assertEqual(im.height, im2.height)

        # new mean should be closer to target mean
        self.assertTrue(abs(im.avg() - 128) > abs(im2.avg() - 128))


if __name__ == '__main__':
    unittest.main()
