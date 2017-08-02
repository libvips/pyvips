# vim: set fileencoding=utf-8 :
# test helpers

import os
import pyvips

IMAGES = os.path.join(os.path.dirname(__file__), 'images')
JPEG_FILE = os.path.join(IMAGES, "йцук.jpg")
SRGB_FILE = os.path.join(IMAGES, "sRGB.icm")

MATLAB_FILE = os.path.join(IMAGES, "sample.mat")
PNG_FILE = os.path.join(IMAGES, "sample.png")
TIF_FILE = os.path.join(IMAGES, "sample.tif")
OME_FILE = os.path.join(IMAGES, "multi-channel-z-series.ome.tif")
ANALYZE_FILE = os.path.join(IMAGES, "t00740_tr1_segm.hdr")
GIF_FILE = os.path.join(IMAGES, "cramps.gif")
WEBP_FILE = os.path.join(IMAGES, "1.webp")
EXR_FILE = os.path.join(IMAGES, "sample.exr")
FITS_FILE = os.path.join(IMAGES, "WFPC2u5780205r_c0fx.fits")
OPENSLIDE_FILE = os.path.join(IMAGES, "CMU-1-Small-Region.svs")
PDF_FILE = os.path.join(IMAGES, "ISO_12233-reschart.pdf")
CMYK_PDF_FILE = os.path.join(IMAGES, "cmyktest.pdf")
SVG_FILE = os.path.join(IMAGES, "vips-profile.svg")
SVGZ_FILE = os.path.join(IMAGES, "vips-profile.svgz")
SVG_GZ_FILE = os.path.join(IMAGES, "vips-profile.svg.gz")
GIF_ANIM_FILE = os.path.join(IMAGES, "cogs.gif")
DICOM_FILE = os.path.join(IMAGES, "dicom_test_image.dcm")

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

# run a 2-ary function on two things -- loop over elements pairwise if the 
# things are lists
def run_fn2(fn, x, y):
    if isinstance(x, pyvips.Image) or isinstance(y, pyvips.Image):
        return fn(x, y)
    elif isinstance(x, list) or isinstance(y, list):
        return [fn(i, j) for i, j in zip_expand(x, y)]
    else:
        return fn(x, y)

