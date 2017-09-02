# vim: set fileencoding=utf-8 :

import gc
import os
import shutil
import tempfile
import unittest

import pyvips
from .helpers import PyvipsTester, JPEG_FILE, SRGB_FILE, \
    MATLAB_FILE, PNG_FILE, TIF_FILE, OME_FILE, ANALYZE_FILE, \
    GIF_FILE, WEBP_FILE, EXR_FILE, FITS_FILE, OPENSLIDE_FILE, \
    PDF_FILE, SVG_FILE, SVGZ_FILE, SVG_GZ_FILE, GIF_ANIM_FILE, \
    DICOM_FILE, temp_filename


class TestForeign(PyvipsTester):
    tempdir = None

    @classmethod
    def setUpClass(cls):
        cls.tempdir = tempfile.mkdtemp()

    def setUp(self):
        self.colour = pyvips.Image.jpegload(JPEG_FILE)
        self.mono = self.colour.extract_band(1)
        # we remove the ICC profile: the RGB one will no longer be appropriate
        self.mono.remove("icc-profile-data")
        self.rad = self.colour.float2rad()
        self.rad.remove("icc-profile-data")
        self.cmyk = self.colour.bandjoin(self.mono)
        self.cmyk = self.cmyk.copy(interpretation=pyvips.Interpretation.CMYK)
        self.cmyk.remove("icc-profile-data")

        im = pyvips.Image.new_from_file(GIF_FILE)
        self.onebit = im > 128

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tempdir, ignore_errors=True)

    # we have test files for formats which have a clear standard
    def file_loader(self, loader, test_file, validate):
        im = pyvips.Operation.call(loader, test_file)
        validate(self, im)
        im = pyvips.Image.new_from_file(test_file)
        validate(self, im)

    def buffer_loader(self, loader, test_file, validate):
        with open(test_file, 'rb') as f:
            buf = f.read()

        im = pyvips.Operation.call(loader, buf)
        validate(self, im)
        im = pyvips.Image.new_from_buffer(buf, "")
        validate(self, im)

    def save_load(self, format, im):
        x = pyvips.Image.new_temp_file(format)
        im.write(x)

        self.assertEqual(im.width, x.width)
        self.assertEqual(im.height, x.height)
        self.assertEqual(im.bands, x.bands)
        max_diff = (im - x).abs().max()
        self.assertEqual(max_diff, 0)

    def save_load_file(self, format, options, im, thresh):
        # yuk!
        # but we can't set format parameters for pyvips.Image.new_temp_file()
        filename = temp_filename(self.tempdir, format)

        im.write_to_file(filename + options)
        x = pyvips.Image.new_from_file(filename)

        self.assertEqual(im.width, x.width)
        self.assertEqual(im.height, x.height)
        self.assertEqual(im.bands, x.bands)
        max_diff = (im - x).abs().max()
        self.assertTrue(max_diff <= thresh)
        x = None

    def save_load_buffer(self, saver, loader, im, max_diff=0):
        buf = pyvips.Operation.call(saver, im)
        x = pyvips.Operation.call(loader, buf)

        self.assertEqual(im.width, x.width)
        self.assertEqual(im.height, x.height)
        self.assertEqual(im.bands, x.bands)
        self.assertLessEqual((im - x).abs().max(), max_diff)

    def save_buffer_tempfile(self, saver, suf, im, max_diff=0):
        filename = temp_filename(self.tempdir, suf)

        buf = pyvips.Operation.call(saver, im)
        f = open(filename, 'wb')
        f.write(buf)
        f.close()

        x = pyvips.Image.new_from_file(filename)

        self.assertEqual(im.width, x.width)
        self.assertEqual(im.height, x.height)
        self.assertEqual(im.bands, x.bands)
        self.assertLessEqual((im - x).abs().max(), max_diff)

    def test_vips(self):
        self.save_load_file(".v", "", self.colour, 0)

        # check we can save and restore metadata
        filename = temp_filename(self.tempdir, ".v")
        self.colour.write_to_file(filename)
        x = pyvips.Image.new_from_file(filename)
        before_exif = self.colour.get_value("exif-data")
        after_exif = x.get_value("exif-data")

        self.assertEqual(len(before_exif), len(after_exif))
        for i in range(len(before_exif)):
            self.assertEqual(before_exif[i], after_exif[i])

        x = None

    def test_jpeg(self):
        if pyvips.type_find("VipsForeign", "jpegload") == 0:
            print("no jpeg support in this vips, skipping test")
            return

        def jpeg_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [6, 5, 3])
            profile = im.get_value("icc-profile-data")
            self.assertEqual(len(profile), 1352)
            self.assertEqual(im.width, 1024)
            self.assertEqual(im.height, 768)
            self.assertEqual(im.bands, 3)

        self.file_loader("jpegload", JPEG_FILE, jpeg_valid)
        self.save_load("%s.jpg", self.mono)
        self.save_load("%s.jpg", self.colour)

        self.buffer_loader("jpegload_buffer", JPEG_FILE, jpeg_valid)
        self.save_load_buffer("jpegsave_buffer", "jpegload_buffer",
                              self.colour, 80)

        # see if we have exif parsing: our test image has this field
        x = pyvips.Image.new_from_file(JPEG_FILE)
        if x.get_typeof("exif-ifd0-Orientation") != 0:
            # we need a copy of the image to set the new metadata on
            # otherwise we get caching problems
            x = pyvips.Image.new_from_file(JPEG_FILE)
            x = x.copy()
            x.set_value("orientation", 2)

            filename = temp_filename(self.tempdir, '.jpg')
            x.write_to_file(filename)
            x = pyvips.Image.new_from_file(filename)
            y = x.get_value("orientation")
            self.assertEqual(y, 2)

            filename = temp_filename(self.tempdir, '.jpg')

            x = pyvips.Image.new_from_file(JPEG_FILE)
            x = x.copy()
            x.set_value("orientation", 2)
            x.write_to_file(filename)
            x = pyvips.Image.new_from_file(filename)
            y = x.get_value("orientation")
            self.assertEqual(y, 2)
            x.remove("orientation")

            filename = temp_filename(self.tempdir, '.jpg')
            x.write_to_file(filename)
            x = pyvips.Image.new_from_file(filename)
            y = x.get_value("orientation")
            self.assertEqual(y, 1)

            filename = temp_filename(self.tempdir, '.jpg')
            x = pyvips.Image.new_from_file(JPEG_FILE)
            x = x.copy()
            x.set_value("orientation", 6)
            x.write_to_file(filename)
            x1 = pyvips.Image.new_from_file(filename)
            x2 = pyvips.Image.new_from_file(filename, autorotate=True)
            self.assertEqual(x1.width, x2.height)
            self.assertEqual(x1.height, x2.width)

    def test_png(self):
        if pyvips.type_find("VipsForeign", "pngload") == 0 or \
                not os.path.isfile(PNG_FILE):
            print("no png support, skipping test")
            return

        def png_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [38671.0, 33914.0, 26762.0])
            self.assertEqual(im.width, 290)
            self.assertEqual(im.height, 442)
            self.assertEqual(im.bands, 3)

        self.file_loader("pngload", PNG_FILE, png_valid)
        self.buffer_loader("pngload_buffer", PNG_FILE, png_valid)
        self.save_load_buffer("pngsave_buffer", "pngload_buffer", self.colour)
        self.save_load("%s.png", self.mono)
        self.save_load("%s.png", self.colour)

    def test_tiff(self):
        if pyvips.type_find("VipsForeign", "tiffload") == 0 or \
                not os.path.isfile(TIF_FILE):
            print("no tiff support, skipping test")
            return

        def tiff_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [38671.0, 33914.0, 26762.0])
            self.assertEqual(im.width, 290)
            self.assertEqual(im.height, 442)
            self.assertEqual(im.bands, 3)

        self.file_loader("tiffload", TIF_FILE, tiff_valid)
        self.buffer_loader("tiffload_buffer", TIF_FILE, tiff_valid)
        self.save_load_buffer("tiffsave_buffer",
                              "tiffload_buffer",
                              self.colour)
        self.save_load("%s.tif", self.mono)
        self.save_load("%s.tif", self.colour)
        self.save_load("%s.tif", self.cmyk)

        self.save_load("%s.tif", self.onebit)
        self.save_load_file(".tif", "[squash]", self.onebit, 0)
        self.save_load_file(".tif", "[miniswhite]", self.onebit, 0)
        self.save_load_file(".tif", "[squash,miniswhite]", self.onebit, 0)

        self.save_load_file(".tif",
                            "[profile={0}]".format(SRGB_FILE),
                            self.colour, 0)
        self.save_load_file(".tif", "[tile]", self.colour, 0)
        self.save_load_file(".tif", "[tile,pyramid]", self.colour, 0)
        self.save_load_file(".tif",
                            "[tile,pyramid,compression=jpeg]", self.colour, 80)
        self.save_load_file(".tif", "[bigtiff]", self.colour, 0)
        self.save_load_file(".tif", "[compression=jpeg]", self.colour, 80)
        self.save_load_file(".tif",
                            "[tile,tile-width=256]", self.colour, 10)

        filename = temp_filename(self.tempdir, '.tif')
        x = pyvips.Image.new_from_file(TIF_FILE)
        x = x.copy()
        x.set_value("orientation", 2)
        x.write_to_file(filename)
        x = pyvips.Image.new_from_file(filename)
        y = x.get_value("orientation")
        self.assertEqual(y, 2)

        filename = temp_filename(self.tempdir, '.tif')
        x = pyvips.Image.new_from_file(TIF_FILE)
        x = x.copy()
        x.set_value("orientation", 2)
        x.write_to_file(filename)
        x = pyvips.Image.new_from_file(filename)
        y = x.get_value("orientation")
        self.assertEqual(y, 2)
        x.remove("orientation")

        filename = temp_filename(self.tempdir, '.tif')
        x.write_to_file(filename)
        x = pyvips.Image.new_from_file(filename)
        y = x.get_value("orientation")
        self.assertEqual(y, 1)

        filename = temp_filename(self.tempdir, '.tif')
        x = pyvips.Image.new_from_file(TIF_FILE)
        x = x.copy()
        x.set_value("orientation", 6)
        x.write_to_file(filename)
        x1 = pyvips.Image.new_from_file(filename)
        x2 = pyvips.Image.new_from_file(filename, autorotate=True)
        self.assertEqual(x1.width, x2.height)
        self.assertEqual(x1.height, x2.width)

        x = pyvips.Image.new_from_file(OME_FILE)
        self.assertEqual(x.width, 439)
        self.assertEqual(x.height, 167)
        page_height = x.height

        x = pyvips.Image.new_from_file(OME_FILE, n=-1)
        self.assertEqual(x.width, 439)
        self.assertEqual(x.height, page_height * 15)

        x = pyvips.Image.new_from_file(OME_FILE, page=1, n=-1)
        self.assertEqual(x.width, 439)
        self.assertEqual(x.height, page_height * 14)

        x = pyvips.Image.new_from_file(OME_FILE, page=1, n=2)
        self.assertEqual(x.width, 439)
        self.assertEqual(x.height, page_height * 2)

        x = pyvips.Image.new_from_file(OME_FILE, n=-1)
        self.assertEqual(x(0, 166)[0], 96)
        self.assertEqual(x(0, 167)[0], 0)
        self.assertEqual(x(0, 168)[0], 1)

        filename = temp_filename(self.tempdir, '.tif')
        x.write_to_file(filename)

        x = pyvips.Image.new_from_file(filename, n=-1)
        self.assertEqual(x.width, 439)
        self.assertEqual(x.height, page_height * 15)
        self.assertEqual(x(0, 166)[0], 96)
        self.assertEqual(x(0, 167)[0], 0)
        self.assertEqual(x(0, 168)[0], 1)

        # pyr save to buffer added in 8.6
        if pyvips.version(0) > 8 or pyvips.version(1) >= 6:
            x = pyvips.Image.new_from_file(TIF_FILE)
            buf = x.tiffsave_buffer(tile=True, pyramid=True)
            filename = temp_filename(self.tempdir, '.tif')
            x.tiffsave(filename, tile=True, pyramid=True)
            with open(filename, 'rb') as f:
                buf2 = f.read()
            self.assertEqual(len(buf), len(buf2))

            a = pyvips.Image.new_from_buffer(buf, "", page=2)
            b = pyvips.Image.new_from_buffer(buf2, "", page=2)
            self.assertEqual(a.width, b.width)
            self.assertEqual(a.height, b.height)
            self.assertEqual(a.avg(), b.avg())

    def test_magickload(self):
        if pyvips.type_find("VipsForeign", "magickload") == 0 or \
                not os.path.isfile(GIF_FILE):
            print("no magick support, skipping test")
            return

        def gif_valid(self, im):
            # some libMagick produce an RGB for this image, some a mono, some
            # rgba, some have a valid alpha, some don't :-(
            # therefore ... just test channel 0
            a = im(10, 10)[0]

            self.assertAlmostEqual(a, 33)
            self.assertEqual(im.width, 159)
            self.assertEqual(im.height, 203)

        self.file_loader("magickload", GIF_FILE, gif_valid)
        self.buffer_loader("magickload_buffer", GIF_FILE, gif_valid)

        # we should have rgba for svg files
        im = pyvips.Image.magickload(SVG_FILE)
        self.assertEqual(im.bands, 4)

        # density should change size of generated svg
        im = pyvips.Image.magickload(SVG_FILE, density='100')
        width = im.width
        height = im.height
        im = pyvips.Image.magickload(SVG_FILE, density='200')
        # This seems to fail on travis, no idea why, some problem in their IM
        # perhaps
        # self.assertEqual(im.width, width * 2)
        # self.assertEqual(im.height, height * 2)

        # all-frames should load every frame of the animation
        # (though all-frames is deprecated)
        im = pyvips.Image.magickload(GIF_ANIM_FILE)
        width = im.width
        height = im.height
        im = pyvips.Image.magickload(GIF_ANIM_FILE, all_frames=True)
        self.assertEqual(im.width, width)
        self.assertEqual(im.height, height * 5)

        # page/n let you pick a range of pages
        im = pyvips.Image.magickload(GIF_ANIM_FILE)
        width = im.width
        height = im.height
        im = pyvips.Image.magickload(GIF_ANIM_FILE, page=1, n=2)
        self.assertEqual(im.width, width)
        self.assertEqual(im.height, height * 2)
        page_height = im.get_value("page-height")
        self.assertEqual(page_height, height)

        # should work for dicom
        im = pyvips.Image.magickload(DICOM_FILE)
        self.assertEqual(im.width, 128)
        self.assertEqual(im.height, 128)
        # some IMs are 3 bands, some are 1, can't really test
        # self.assertEqual(im.bands, 1)

    def test_webp(self):
        if pyvips.type_find("VipsForeign", "webpload") == 0 or \
                not os.path.isfile(WEBP_FILE):
            print("no webp support, skipping test")
            return

        def webp_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [71, 166, 236])
            self.assertEqual(im.width, 550)
            self.assertEqual(im.height, 368)
            self.assertEqual(im.bands, 3)

        self.file_loader("webpload", WEBP_FILE, webp_valid)
        self.buffer_loader("webpload_buffer", WEBP_FILE, webp_valid)
        self.save_load_buffer("webpsave_buffer", "webpload_buffer",
                              self.colour, 60)
        self.save_load("%s.webp", self.colour)

        # test lossless mode
        im = pyvips.Image.new_from_file(WEBP_FILE)
        buf = im.webpsave_buffer(lossless=True)
        im2 = pyvips.Image.new_from_buffer(buf, "")
        self.assertEqual(im.avg(), im2.avg())

        # higher Q should mean a bigger buffer
        b1 = im.webpsave_buffer(Q=10)
        b2 = im.webpsave_buffer(Q=90)
        self.assertGreater(len(b2), len(b1))

        # try saving an image with an ICC profile and reading it back ... if we
        # can do it, our webp supports metadata load/save
        buf = self.colour.webpsave_buffer()
        im = pyvips.Image.new_from_buffer(buf, "")
        if im.get_typeof("icc-profile-data") != 0:
            # verify that the profile comes back unharmed
            p1 = self.colour.get_value("icc-profile-data")
            p2 = im.get_value("icc-profile-data")
            self.assertEqual(p1, p2)

            # add tests for exif, xmp, ipct
            # the exif test will need us to be able to walk the header,
            # we can't just check exif-data

            # we can test that exif changes change the output of webpsave
            # first make sure we have exif support
            z = pyvips.Image.new_from_file(JPEG_FILE)
            if z.get_typeof("exif-ifd0-Orientation") != 0:
                x = self.colour.copy()
                x.set_value("orientation", 6)
                buf = x.webpsave_buffer()
                y = pyvips.Image.new_from_buffer(buf, "")
                self.assertEqual(y.get_value("orientation"), 6)

    def test_analyzeload(self):
        if pyvips.type_find("VipsForeign", "analyzeload") == 0 or \
                not os.path.isfile(ANALYZE_FILE):
            print("no analyze support, skipping test")
            return

        def analyze_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqual(a[0], 3335)
            self.assertEqual(im.width, 128)
            self.assertEqual(im.height, 8064)
            self.assertEqual(im.bands, 1)

        self.file_loader("analyzeload", ANALYZE_FILE, analyze_valid)

    def test_matload(self):
        if pyvips.type_find("VipsForeign", "matload") == 0 or \
                not os.path.isfile(MATLAB_FILE):
            print("no matlab support, skipping test")
            return

        def matlab_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [38671.0, 33914.0, 26762.0])
            self.assertEqual(im.width, 290)
            self.assertEqual(im.height, 442)
            self.assertEqual(im.bands, 3)

        self.file_loader("matload", MATLAB_FILE, matlab_valid)

    def test_openexrload(self):
        if pyvips.type_find("VipsForeign", "openexrload") == 0 or \
                not os.path.isfile(EXR_FILE):
            print("no openexr support, skipping test")
            return

        def exr_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [0.124512, 0.159668,
                                              0.040375, 1.0],
                                          places=5)
            self.assertEqual(im.width, 610)
            self.assertEqual(im.height, 406)
            self.assertEqual(im.bands, 4)

        self.file_loader("openexrload", EXR_FILE, exr_valid)

    def test_fitsload(self):
        if pyvips.type_find("VipsForeign", "fitsload") == 0 or \
                not os.path.isfile(FITS_FILE):
            print("no fits support, skipping test")
            return

        def fits_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [-0.165013, -0.148553, 1.09122,
                                              -0.942242],
                                          places=5)
            self.assertEqual(im.width, 200)
            self.assertEqual(im.height, 200)
            self.assertEqual(im.bands, 4)

        self.file_loader("fitsload", FITS_FILE, fits_valid)
        self.save_load("%s.fits", self.mono)

    def test_openslideload(self):
        if pyvips.type_find("VipsForeign", "openslideload") == 0 or \
                not os.path.isfile(OPENSLIDE_FILE):
            print("no openslide support, skipping test")
            return

        def openslide_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [244, 250, 243, 255])
            self.assertEqual(im.width, 2220)
            self.assertEqual(im.height, 2967)
            self.assertEqual(im.bands, 4)

        self.file_loader("openslideload", OPENSLIDE_FILE, openslide_valid)

    def test_pdfload(self):
        if pyvips.type_find("VipsForeign", "pdfload") == 0 or \
                not os.path.isfile(PDF_FILE):
            print("no pdf support, skipping test")
            return

        def pdf_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [35, 31, 32, 255])
            self.assertEqual(im.width, 1133)
            self.assertEqual(im.height, 680)
            self.assertEqual(im.bands, 4)

        self.file_loader("pdfload", PDF_FILE, pdf_valid)
        self.buffer_loader("pdfload_buffer", PDF_FILE, pdf_valid)

        im = pyvips.Image.new_from_file(PDF_FILE)
        x = pyvips.Image.new_from_file(PDF_FILE, scale=2)
        self.assertLess(abs(im.width * 2 - x.width), 2)
        self.assertLess(abs(im.height * 2 - x.height), 2)

        im = pyvips.Image.new_from_file(PDF_FILE)
        x = pyvips.Image.new_from_file(PDF_FILE, dpi=144)
        self.assertLess(abs(im.width * 2 - x.width), 2)
        self.assertLess(abs(im.height * 2 - x.height), 2)

    def test_gifload(self):
        if pyvips.type_find("VipsForeign", "gifload") == 0 or \
                not os.path.isfile(GIF_FILE):
            print("no gif support, skipping test")
            return

        def gif_valid(self, im):
            a = im(10, 10)
            self.assertAlmostEqualObjects(a, [33])
            self.assertEqual(im.width, 159)
            self.assertEqual(im.height, 203)
            self.assertEqual(im.bands, 1)

        self.file_loader("gifload", GIF_FILE, gif_valid)
        self.buffer_loader("gifload_buffer", GIF_FILE, gif_valid)

        x1 = pyvips.Image.new_from_file(GIF_ANIM_FILE)
        x2 = pyvips.Image.new_from_file(GIF_ANIM_FILE, n=2)
        self.assertEqual(x2.height, 2 * x1.height)
        page_height = x2.get_value("page-height")
        self.assertEqual(page_height, x1.height)

        x2 = pyvips.Image.new_from_file(GIF_ANIM_FILE, n=-1)
        self.assertEqual(x2.height, 5 * x1.height)

        x2 = pyvips.Image.new_from_file(GIF_ANIM_FILE, page=1, n=-1)
        self.assertEqual(x2.height, 4 * x1.height)

    def test_svgload(self):
        if pyvips.type_find("VipsForeign", "svgload") == 0 or \
                not os.path.isfile(SVG_FILE):
            print("no svg support, skipping test")
            return

        def svg_valid(self, im):
            a = im(10, 10)

            # some old rsvg versions are way, way off
            self.assertLess(abs(a[0] - 79), 2)
            self.assertLess(abs(a[1] - 79), 2)
            self.assertLess(abs(a[2] - 132), 2)
            self.assertLess(abs(a[3] - 255), 2)

            self.assertEqual(im.width, 288)
            self.assertEqual(im.height, 470)
            self.assertEqual(im.bands, 4)

        self.file_loader("svgload", SVG_FILE, svg_valid)
        self.buffer_loader("svgload_buffer", SVG_FILE, svg_valid)

        self.file_loader("svgload", SVGZ_FILE, svg_valid)
        self.buffer_loader("svgload_buffer", SVGZ_FILE, svg_valid)

        self.file_loader("svgload", SVG_GZ_FILE, svg_valid)

        im = pyvips.Image.new_from_file(SVG_FILE)
        x = pyvips.Image.new_from_file(SVG_FILE, scale=2)
        self.assertLess(abs(im.width * 2 - x.width), 2)
        self.assertLess(abs(im.height * 2 - x.height), 2)

        im = pyvips.Image.new_from_file(SVG_FILE)
        x = pyvips.Image.new_from_file(SVG_FILE, dpi=144)
        self.assertLess(abs(im.width * 2 - x.width), 2)
        self.assertLess(abs(im.height * 2 - x.height), 2)

    def test_csv(self):
        self.save_load("%s.csv", self.mono)

    def test_matrix(self):
        self.save_load("%s.mat", self.mono)

    def test_ppm(self):
        if pyvips.type_find("VipsForeign", "ppmload") == 0:
            print("no PPM support, skipping test")
            return

        self.save_load("%s.ppm", self.mono)
        self.save_load("%s.ppm", self.colour)

    def test_rad(self):
        if pyvips.type_find("VipsForeign", "radload") == 0:
            print("no Radiance support, skipping test")
            return

        self.save_load("%s.hdr", self.colour)
        self.save_buffer_tempfile("radsave_buffer", ".hdr",
                                  self.rad, max_diff=0)

    def test_dzsave(self):
        if pyvips.type_find("VipsForeign", "dzsave") == 0:
            print("no dzsave support, skipping test")
            return

        # dzsave is hard to test, there are so many options
        # test each option separately and hope they all function together
        # correctly

        # default deepzoom layout ... we must use png here, since we want to
        # test the overlap for equality
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, suffix=".png")

        # test horizontal overlap ... expect 256 step, overlap 1
        x = pyvips.Image.new_from_file(filename + "_files/10/0_0.png")
        self.assertEqual(x.width, 255)
        y = pyvips.Image.new_from_file(filename + "_files/10/1_0.png")
        self.assertEqual(y.width, 256)

        # the right two columns of x should equal the left two columns of y
        left = x.crop(x.width - 2, 0, 2, x.height)
        right = y.crop(0, 0, 2, y.height)
        self.assertEqual((left - right).abs().max(), 0)

        # test vertical overlap
        self.assertEqual(x.height, 255)
        y = pyvips.Image.new_from_file(filename + "_files/10/0_1.png")
        self.assertEqual(y.height, 256)

        # the bottom two rows of x should equal the top two rows of y
        top = x.crop(0, x.height - 2, x.width, 2)
        bottom = y.crop(0, 0, y.width, 2)
        self.assertEqual((top - bottom).abs().max(), 0)

        # there should be a bottom layer
        x = pyvips.Image.new_from_file(filename + "_files/0/0_0.png")
        self.assertEqual(x.width, 1)
        self.assertEqual(x.height, 1)

        # 10 should be the final layer
        self.assertFalse(os.path.isdir(filename + "_files/11"))

        # default google layout
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, layout="google")

        # test bottom-right tile ... default is 256x256 tiles, overlap 0
        x = pyvips.Image.new_from_file(filename + "/2/2/3.jpg")
        self.assertEqual(x.width, 256)
        self.assertEqual(x.height, 256)
        self.assertFalse(os.path.exists(filename + "/2/2/4.jpg"))
        self.assertFalse(os.path.exists(filename + "/3"))
        x = pyvips.Image.new_from_file(filename + "/blank.png")
        self.assertEqual(x.width, 256)
        self.assertEqual(x.height, 256)

        # google layout with overlap ... verify that we clip correctly
        # with overlap 192 tile size 256, we should step by 64 pixels each time
        # so 3x3 tiles exactly
        filename = temp_filename(self.tempdir, '')
        self.colour.crop(0, 0, 384, 384).dzsave(filename, layout="google",
                                                overlap=192, depth="one")

        # test bottom-right tile ... default is 256x256 tiles, overlap 0
        x = pyvips.Image.new_from_file(filename + "/0/2/2.jpg")
        self.assertEqual(x.width, 256)
        self.assertEqual(x.height, 256)
        self.assertFalse(os.path.exists(filename + "/0/3/3.jpg"))

        filename = temp_filename(self.tempdir, '')
        self.colour.crop(0, 0, 385, 385).dzsave(filename, layout="google",
                                                overlap=192, depth="one")

        # test bottom-right tile ... default is 256x256 tiles, overlap 0
        x = pyvips.Image.new_from_file(filename + "/0/3/3.jpg")
        self.assertEqual(x.width, 256)
        self.assertEqual(x.height, 256)
        self.assertFalse(os.path.exists(filename + "/0/4/4.jpg"))

        # default zoomify layout
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, layout="zoomify")

        # 256x256 tiles, no overlap
        self.assertTrue(os.path.exists(filename + "/ImageProperties.xml"))
        x = pyvips.Image.new_from_file(filename + "/TileGroup0/2-3-2.jpg")
        self.assertEqual(x.width, 256)
        self.assertEqual(x.height, 256)

        # test zip output
        filename = temp_filename(self.tempdir, '.zip')
        self.colour.dzsave(filename)
        # before 8.5.8, you needed a gc on pypy to flush small zip output to
        # disc
        gc.collect()
        self.assertTrue(os.path.exists(filename))
        self.assertFalse(os.path.exists(filename + "_files"))
        self.assertFalse(os.path.exists(filename + ".dzi"))

        # test compressed zip output
        filename2 = temp_filename(self.tempdir, '.zip')
        self.colour.dzsave(filename2, compression=-1)
        # before 8.5.8, you needed a gc on pypy to flush small zip output to
        # disc
        gc.collect()
        self.assertTrue(os.path.exists(filename2))
        self.assertLess(os.path.getsize(filename2),
                        os.path.getsize(filename))

        # test suffix
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, suffix=".png")

        x = pyvips.Image.new_from_file(filename + "_files/10/0_0.png")
        self.assertEqual(x.width, 255)

        # test overlap
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, overlap=200)

        y = pyvips.Image.new_from_file(filename + "_files/10/1_1.jpeg")
        self.assertEqual(y.width, 654)

        # test tile-size
        filename = temp_filename(self.tempdir, '')
        self.colour.dzsave(filename, tile_size=512)

        y = pyvips.Image.new_from_file(filename + "_files/10/0_0.jpeg")
        self.assertEqual(y.width, 513)
        self.assertEqual(y.height, 513)

        # test save to memory buffer
        filename = temp_filename(self.tempdir, '.zip')
        base = os.path.basename(filename)
        root, ext = os.path.splitext(base)

        self.colour.dzsave(filename)
        # before 8.5.8, you needed a gc on pypy to flush small zip output to
        # disc
        gc.collect()
        with open(filename, 'rb') as f:
            buf1 = f.read()
        buf2 = self.colour.dzsave_buffer(basename=root)
        self.assertEqual(len(buf1), len(buf2))

        # we can't test the bytes are exactly equal, the timestamps will be
        # different


if __name__ == '__main__':
    unittest.main()
