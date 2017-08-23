# vim: set fileencoding=utf-8 :
# test helpers
from __future__ import division

import os
import tempfile
import unittest

import pyvips

IMAGES = os.path.join(os.path.dirname(__file__), 'images')
JPEG_FILE = os.path.join(IMAGES, "йцук.jpg")
SRGB_FILE = os.path.join(IMAGES, "sRGB.icm")

TEST_IMAGES = os.path.join(os.path.dirname(__file__),
                           '..', '..', 'test_images')
MATLAB_FILE = os.path.join(TEST_IMAGES, "sample.mat")
PNG_FILE = os.path.join(TEST_IMAGES, "sample.png")
TIF_FILE = os.path.join(TEST_IMAGES, "sample.tif")
OME_FILE = os.path.join(TEST_IMAGES, "multi-channel-z-series.ome.tif")
ANALYZE_FILE = os.path.join(TEST_IMAGES, "t00740_tr1_segm.hdr")
GIF_FILE = os.path.join(TEST_IMAGES, "cramps.gif")
WEBP_FILE = os.path.join(TEST_IMAGES, "1.webp")
EXR_FILE = os.path.join(TEST_IMAGES, "sample.exr")
FITS_FILE = os.path.join(TEST_IMAGES, "WFPC2u5780205r_c0fx.fits")
OPENSLIDE_FILE = os.path.join(TEST_IMAGES, "CMU-1-Small-Region.svs")
PDF_FILE = os.path.join(TEST_IMAGES, "ISO_12233-reschart.pdf")
CMYK_PDF_FILE = os.path.join(TEST_IMAGES, "cmyktest.pdf")
SVG_FILE = os.path.join(TEST_IMAGES, "vips-profile.svg")
SVGZ_FILE = os.path.join(TEST_IMAGES, "vips-profile.svgz")
SVG_GZ_FILE = os.path.join(TEST_IMAGES, "vips-profile.svg.gz")
GIF_ANIM_FILE = os.path.join(TEST_IMAGES, "cogs.gif")
DICOM_FILE = os.path.join(TEST_IMAGES, "dicom_test_image.dcm")

unsigned_formats = [pyvips.BandFormat.UCHAR,
                    pyvips.BandFormat.USHORT,
                    pyvips.BandFormat.UINT]
signed_formats = [pyvips.BandFormat.CHAR,
                  pyvips.BandFormat.SHORT,
                  pyvips.BandFormat.INT]
float_formats = [pyvips.BandFormat.FLOAT,
                 pyvips.BandFormat.DOUBLE]
complex_formats = [pyvips.BandFormat.COMPLEX,
                   pyvips.BandFormat.DPCOMPLEX]
int_formats = unsigned_formats + signed_formats
noncomplex_formats = int_formats + float_formats
all_formats = int_formats + float_formats + complex_formats

colour_colourspaces = [pyvips.Interpretation.XYZ,
                       pyvips.Interpretation.LAB,
                       pyvips.Interpretation.LCH,
                       pyvips.Interpretation.CMC,
                       pyvips.Interpretation.LABS,
                       pyvips.Interpretation.SCRGB,
                       pyvips.Interpretation.HSV,
                       pyvips.Interpretation.SRGB,
                       pyvips.Interpretation.YXY]
coded_colourspaces = [pyvips.Interpretation.LABQ]
mono_colourspaces = [pyvips.Interpretation.B_W]
sixteenbit_colourspaces = [pyvips.Interpretation.GREY16,
                           pyvips.Interpretation.RGB16]
all_colourspaces = colour_colourspaces + mono_colourspaces + \
                   coded_colourspaces + sixteenbit_colourspaces

max_value = {pyvips.BandFormat.UCHAR: 0xff,
             pyvips.BandFormat.USHORT: 0xffff,
             pyvips.BandFormat.UINT: 0xffffffff,
             pyvips.BandFormat.CHAR: 0x7f,
             pyvips.BandFormat.SHORT: 0x7fff,
             pyvips.BandFormat.INT: 0x7fffffff,
             pyvips.BandFormat.FLOAT: 1.0,
             pyvips.BandFormat.DOUBLE: 1.0,
             pyvips.BandFormat.COMPLEX: 1.0,
             pyvips.BandFormat.DPCOMPLEX: 1.0}

sizeof_format = {pyvips.BandFormat.UCHAR: 1,
                 pyvips.BandFormat.USHORT: 2,
                 pyvips.BandFormat.UINT: 4,
                 pyvips.BandFormat.CHAR: 1,
                 pyvips.BandFormat.SHORT: 2,
                 pyvips.BandFormat.INT: 4,
                 pyvips.BandFormat.FLOAT: 4,
                 pyvips.BandFormat.DOUBLE: 8,
                 pyvips.BandFormat.COMPLEX: 8,
                 pyvips.BandFormat.DPCOMPLEX: 16}

rot45_angles = [pyvips.Angle45.D0,
                pyvips.Angle45.D45,
                pyvips.Angle45.D90,
                pyvips.Angle45.D135,
                pyvips.Angle45.D180,
                pyvips.Angle45.D225,
                pyvips.Angle45.D270,
                pyvips.Angle45.D315]

rot45_angle_bonds = [pyvips.Angle45.D0,
                     pyvips.Angle45.D315,
                     pyvips.Angle45.D270,
                     pyvips.Angle45.D225,
                     pyvips.Angle45.D180,
                     pyvips.Angle45.D135,
                     pyvips.Angle45.D90,
                     pyvips.Angle45.D45]

rot_angles = [pyvips.Angle.D0,
              pyvips.Angle.D90,
              pyvips.Angle.D180,
              pyvips.Angle.D270]

rot_angle_bonds = [pyvips.Angle.D0,
                   pyvips.Angle.D270,
                   pyvips.Angle.D180,
                   pyvips.Angle.D90]


# an expanding zip ... if either of the args is a scalar or a one-element list,
# duplicate it down the other side
def zip_expand(x, y):
    # handle singleton list case
    if isinstance(x, list) and len(x) == 1:
        x = x[0]
    if isinstance(y, list) and len(y) == 1:
        y = y[0]

    if isinstance(x, list) and isinstance(y, list):
        return list(zip(x, y))
    elif isinstance(x, list):
        return [[i, y] for i in x]
    elif isinstance(y, list):
        return [[x, j] for j in y]
    else:
        return [[x, y]]


# run a 1-ary function on a thing -- loop over elements if the
# thing is a list
def run_fn(fn, x):
    if isinstance(x, list):
        return [fn(i) for i in x]
    else:
        return fn(x)


# make a temp filename with the specified suffix and in the
# specified directory
def temp_filename(directory, suffix):
    temp_name = next(tempfile._get_candidate_names())
    filename = os.path.join(directory, temp_name + suffix)

    return filename


# run a 2-ary function on two things -- loop over elements pairwise if the
# things are lists
def run_fn2(fn, x, y):
    if isinstance(x, pyvips.Image) or isinstance(y, pyvips.Image):
        return fn(x, y)
    elif isinstance(x, list) or isinstance(y, list):
        return [fn(i, j) for i, j in zip_expand(x, y)]
    else:
        return fn(x, y)


class PyvipsTester(unittest.TestCase):
    # test a pair of things which can be lists for approx. equality
    def assertAlmostEqualObjects(self, a, b, places=4, msg=''):
        # print 'assertAlmostEqualObjects %s = %s' % (a, b)
        for x, y in zip_expand(a, b):
            self.assertAlmostEqual(x, y, places=places, msg=msg)

    # test a pair of things which can be lists for equality
    def assertEqualObjects(self, a, b, places=4, msg=''):
        # print 'assertEqualObjects %s = %s' % (a, b)
        for x, y in zip_expand(a, b):
            self.assertEqual(x, y, msg=msg)

    # test a pair of things which can be lists for difference less than a
    # threshold
    def assertLessThreshold(self, a, b, diff):
        for x, y in zip_expand(a, b):
            self.assertLess(abs(x - y), diff)

    # run a function on an image and on a single pixel, the results
    # should match
    def run_cmp(self, message, im, x, y, fn):
        a = im(x, y)
        v1 = fn(a)
        im2 = fn(im)
        v2 = im2(x, y)
        self.assertAlmostEqualObjects(v1, v2, msg=message)

    # run a function on an image,
    # 50,50 and 10,10 should have different values on the test image
    def run_image(self, message, im, fn):
        self.run_cmp(message, im, 50, 50, fn)
        self.run_cmp(message, im, 10, 10, fn)

    # run a function on (image, constant), and on (constant, image).
    # 50,50 and 10,10 should have different values on the test image
    def run_const(self, message, fn, im, c):
        self.run_cmp(message, im, 50, 50, lambda x: run_fn2(fn, x, c))
        self.run_cmp(message, im, 50, 50, lambda x: run_fn2(fn, c, x))
        self.run_cmp(message, im, 10, 10, lambda x: run_fn2(fn, x, c))
        self.run_cmp(message, im, 10, 10, lambda x: run_fn2(fn, c, x))

    # run a function on a pair of images and on a pair of pixels, the results
    # should match
    def run_cmp2(self, message, left, right, x, y, fn):
        a = left(x, y)
        b = right(x, y)
        v1 = fn(a, b)
        after = fn(left, right)
        v2 = after(x, y)
        self.assertAlmostEqualObjects(v1, v2, msg=message)

    # run a function on a pair of images
    # 50,50 and 10,10 should have different values on the test image
    def run_image2(self, message, left, right, fn):
        self.run_cmp2(message, left, right, 50, 50,
                      lambda x, y: run_fn2(fn, x, y))
        self.run_cmp2(message, left, right, 10, 10,
                      lambda x, y: run_fn2(fn, x, y))
