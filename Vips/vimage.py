# wrap VipsOperation

import numbers

from Vips import *

ffi.cdef('''
    typedef struct _VipsImage {
        VipsObject parent_instance;

        // opaque
    } VipsImage;

    const char* vips_foreign_find_load (const char* name);
    const char* vips_foreign_find_load_buffer (const void* data, size_t size);
    const char* vips_foreign_find_save (const char* name);
    const char* vips_foreign_find_save_buffer (const char* suffix);

    VipsImage* vips_image_new_matrix_from_array (int width, int height,
            const double* array, int size);

    VipsImage* vips_image_copy_memory (VipsImage* image);

    GType vips_image_get_typeof (const VipsImage* image, 
        const char* name);
    int vips_image_get (const VipsImage* image, 
        const char* name, GValue* value_copy);
    void vips_image_set (VipsImage* image, const char* name, GValue* value);
    int vips_image_remove (VipsImage* image, const char* name);

    char* vips_filename_get_filename (const char* vips_filename);
    char* vips_filename_get_options (const char* vips_filename);

''')

# either a single number, or a table of numbers
def is_pixel(value):
    return (isinstance(value, numbers.Number) or 
            (isinstance(vaue, list) and not isinstance(value, Image)))

# test for rectangular array of something
def is_2D(array):
    if not isinstance(array, list):
        return False

    for x in array:
        if not isinstance(x, list):
            return False
        if len(x) != len(array[0]):
            return False

    return True

def swap_Image_left(left, right):
    if isinstance(left, Image):
        return left, right
    elif isinstance(right, Image):
        return right, left
    else:
        error('must have one image argument')

def call_enum(image, other, base, operation):
    if isinstance(other, numbers.Number):
        return Operation.call(base + '_const', image, operation, [other])
    elif is_pixel(other):
        return Operation.call(base + '_const', image, operation, other)
    else:
        return Operation.call(base, image, other, operation)

class Image(VipsObject):

    @staticmethod
    def imageize(self, value):
        # careful! self can be None if value is a 2D array
        if isinstance(value, Image):
            return value
        elif is_2D(value):
            return Image.new_from_array(value)
        else:
            return self.new_from_image(value)

    def __init__(self, pointer):
        log('Image.__init__: pointer = {0}'.format(pointer))
        super(Image, self).__init__(pointer)

    @staticmethod
    def new_from_file(vips_filename, **kwargs):
        filename = vips_lib.vips_filename_get_filename(vips_filename)
        options = vips_lib.vips_filename_get_options(vips_filename)
        name = vips_lib.vips_foreign_find_load(filename)
        if name == ffi.NULL:
            vips_error()

        return Operation.call(ffi.string(name), ffi.string(filename), 
                string_options = ffi.string(options), **kwargs)

banana = Image
