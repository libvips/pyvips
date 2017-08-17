# vim: set fileencoding=utf-8 :
import unittest

import pyvips
from .helpers import PyvipsTester, JPEG_FILE


class TestGValue(PyvipsTester):
    def test_bool(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.gbool_type)
        gv.set(True)
        value = gv.get()
        self.assertEqual(value, True)

        gv.set(False)
        value = gv.get()
        self.assertEqual(value, False)

    def test_int(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.gint_type)
        gv.set(12)
        value = gv.get()
        self.assertEqual(value, 12)

    def test_double(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.gdouble_type)
        gv.set(3.1415)
        value = gv.get()
        self.assertEqual(value, 3.1415)

    def test_enum(self):
        # the Interpretation enum is created when the first image is made --
        # make it ourselves in case we are run before the first image
        pyvips.vips_lib.vips_interpretation_get_type()
        interpretation_gtype = pyvips.gobject_lib. \
            g_type_from_name(b'VipsInterpretation')
        gv = pyvips.GValue()
        gv.set_type(interpretation_gtype)
        gv.set('xyz')
        value = gv.get()
        self.assertEqual(value, 'xyz')

    def test_flags(self):
        # the OperationFlags enum is created when the first op is made --
        # make it ourselves in case we are run before that
        pyvips.vips_lib.vips_operation_flags_get_type()
        operationflags_gtype = pyvips.gobject_lib. \
            g_type_from_name(b'VipsOperationFlags')
        gv = pyvips.GValue()
        gv.set_type(operationflags_gtype)
        gv.set(12)
        value = gv.get()
        self.assertEqual(value, 12)

    def test_string(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.gstr_type)
        gv.set('banana')
        value = gv.get()
        self.assertEqual(value, 'banana')

    def test_array_int(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.array_int_type)
        gv.set([1, 2, 3])
        value = gv.get()
        self.assertAlmostEqualObjects(value, [1, 2, 3])

    def test_array_double(self):
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.array_double_type)
        gv.set([1.1, 2.1, 3.1])
        value = gv.get()
        self.assertAlmostEqualObjects(value, [1.1, 2.1, 3.1])

    def test_image(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.image_type)
        gv.set(image)
        value = gv.get()
        self.assertEqual(value, image)

    def test_array_image(self):
        image = pyvips.Image.new_from_file(JPEG_FILE)
        r, g, b = image.bandsplit()
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.array_image_type)
        gv.set([r, g, b])
        value = gv.get()
        self.assertEqual(value, [r, g, b])

    def test_blob(self):
        with open(JPEG_FILE, 'rb') as f:
            blob = f.read()
        gv = pyvips.GValue()
        gv.set_type(pyvips.GValue.blob_type)
        gv.set(blob)
        value = gv.get()
        self.assertEqual(value, blob)


if __name__ == '__main__':
    unittest.main()
