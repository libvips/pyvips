# vim: set fileencoding=utf-8 :
# test helpers
import os
import tempfile
import pytest

import pyvips

IMAGES = os.path.join(os.path.dirname(__file__), os.pardir, 'images')
JPEG_FILE = os.path.join(IMAGES, "sample.jpg")
WEBP_FILE = os.path.join(IMAGES, "sample.webp")
SVG_FILE = os.path.join(IMAGES, "logo.svg")


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


# test for an operator exists
def have(name):
    return pyvips.type_find("VipsOperation", name) != 0


# use as @skip_if_no('jpegload')
def skip_if_no(operator_name):
    return pytest.mark.skipif(not have(operator_name),
                              reason=('no {}, skipping test'.
                                      format(operator_name)))


# run a 2-ary function on two things -- loop over elements pairwise if the
# things are lists
def run_fn2(fn, x, y):
    if isinstance(x, pyvips.Image) or isinstance(y, pyvips.Image):
        return fn(x, y)
    elif isinstance(x, list) or isinstance(y, list):
        return [fn(i, j) for i, j in zip_expand(x, y)]
    else:
        return fn(x, y)


# test a pair of things which can be lists for approx. equality
def assert_almost_equal_objects(a, b, threshold=0.0001, msg=''):
    # print(f'assertAlmostEqualObjects {a} = {b}')
    assert all([pytest.approx(x, abs=threshold) == y
                for x, y in zip_expand(a, b)]), msg


# test a pair of things which can be lists for equality
def assert_equal_objects(a, b, msg=''):
    # print(f'assertEqualObjects {a} = {b}')
    assert all([x == y for x, y in zip_expand(a, b)]), msg


# test a pair of things which can be lists for difference less than a
# threshold
def assert_less_threshold(a, b, diff):
    assert all([abs(x - y) < diff for x, y in zip_expand(a, b)])


# run a function on an image and on a single pixel, the results
# should match
def run_cmp(message, im, x, y, fn):
    a = im(x, y)
    v1 = fn(a)
    im2 = fn(im)
    v2 = im2(x, y)
    assert_almost_equal_objects(v1, v2, msg=message)


# run a function on an image,
# 50,50 and 10,10 should have different values on the test image
def run_image(message, im, fn):
    run_cmp(message, im, 50, 50, fn)
    run_cmp(message, im, 10, 10, fn)


# run a function on (image, constant), and on (constant, image).
# 50,50 and 10,10 should have different values on the test image
def run_const(message, fn, im, c):
    run_cmp(message, im, 50, 50, lambda x: run_fn2(fn, x, c))
    run_cmp(message, im, 50, 50, lambda x: run_fn2(fn, c, x))
    run_cmp(message, im, 10, 10, lambda x: run_fn2(fn, x, c))
    run_cmp(message, im, 10, 10, lambda x: run_fn2(fn, c, x))


# run a function on a pair of images and on a pair of pixels, the results
# should match
def run_cmp2(message, left, right, x, y, fn):
    a = left(x, y)
    b = right(x, y)
    v1 = fn(a, b)
    after = fn(left, right)
    v2 = after(x, y)
    assert_almost_equal_objects(v1, v2, msg=message)


# run a function on a pair of images
# 50,50 and 10,10 should have different values on the test image
def run_image2(message, left, right, fn):
    run_cmp2(message, left, right, 50, 50,
             lambda x, y: run_fn2(fn, x, y))
    run_cmp2(message, left, right, 10, 10,
             lambda x, y: run_fn2(fn, x, y))
