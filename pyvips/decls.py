# all the C decls for pyvips

# we keep these together to make switching between ABI and API modes simpler

# we have to pass in the libvips version, since it can come from either
# pkg-config in compile.py (in API mode) or libvips itself in __init__.py
# (in ABI mode)

import sys


def _at_least(features, x, y):
    return features['major'] > x or (features['major'] == x and
                                     features['minor'] >= y)


def cdefs(features):
    """Return the C API declarations for libvips.

    features is a dict with the features we want. Some featrures were only
    added in later libvipsm for example, and some need to be disabled in
    some FFI modes.
    """

    code = ''

    # apparently the safest way to do this
    is_64bits = sys.maxsize > 2 ** 32

    # GType is an int the size of a pointer ... I don't think we can just use
    # size_t, sadly
    if is_64bits:
        code += '''
            typedef uint64_t GType;
        '''
    else:
        code += '''
            typedef uint32_t GType;
        '''

    code += '''
        typedef void (*GLogFunc) (const char* log_domain,
            int log_level,
            const char* message, void* user_data);
        int g_log_set_handler (const char* log_domain,
            int log_levels,
            GLogFunc log_func, void* user_data);

        void g_log_remove_handler (const char* log_domain, int handler_id);

        typedef struct _VipsImage VipsImage;
        typedef struct _GValue GValue;

        void* g_malloc (size_t size);
        void g_free (void* data);
        int vips_free (void* a);

        void vips_leak_set (int leak);

        char* vips_path_filename7 (const char* path);
        char* vips_path_mode7 (const char* path);

        GType vips_type_find (const char* basename, const char* nickname);
        const char* vips_nickname_find (GType type);

        const char* g_type_name (GType gtype);
        GType g_type_from_name (const char* name);

        typedef void* (*VipsTypeMap2Fn) (GType type, void* a, void* b);
        void* vips_type_map (GType base, VipsTypeMap2Fn fn, void* a, void* b);

        const char* vips_error_buffer (void);
        void vips_error_clear (void);

        typedef struct _GValue {
            GType g_type;
            uint64_t data[2];
        } GValue;

        void g_value_init (GValue* value, GType gtype);
        void g_value_unset (GValue* value);
        GType g_type_fundamental (GType gtype);

        int vips_enum_from_nick (const char* domain,
            GType gtype, const char* str);
        const char *vips_enum_nick (GType gtype, int value);

        void g_value_set_boolean (GValue* value, int v_boolean);
        void g_value_set_int (GValue* value, int i);
        void g_value_set_double (GValue* value, double d);
        void g_value_set_enum (GValue* value, int e);
        void g_value_set_flags (GValue* value, unsigned int f);
        void g_value_set_string (GValue* value, const char* str);
        void vips_value_set_ref_string (GValue* value, const char* str);
        void g_value_set_object (GValue* value, void* object);
        void vips_value_set_array_double (GValue* value,
            const double* array, int n );
        void vips_value_set_array_int (GValue* value,
            const int* array, int n );
        void vips_value_set_array_image (GValue *value, int n);
        typedef int (*VipsCallbackFn)(void* a, void* b);
        void vips_value_set_blob (GValue* value,
            VipsCallbackFn free_fn, void* data, size_t length);

        int g_value_get_boolean (const GValue* value);
        int g_value_get_int (GValue* value);
        double g_value_get_double (GValue* value);
        int g_value_get_enum (GValue* value);
        unsigned int g_value_get_flags (GValue* value);
        const char* g_value_get_string (GValue* value);
        const char* vips_value_get_ref_string (const GValue* value,
            size_t* length);
        void* g_value_get_object (GValue* value);
        double* vips_value_get_array_double (const GValue* value, int* n);
        int* vips_value_get_array_int (const GValue* value, int* n);
        VipsImage** vips_value_get_array_image (const GValue* value, int* n);
        void* vips_value_get_blob (const GValue* value, size_t* length);

        // need to make some of these by hand
        GType vips_interpretation_get_type (void);
        GType vips_operation_flags_get_type (void);
        GType vips_band_format_get_type (void);
        GType vips_token_get_type (void);
        GType vips_saveable_get_type (void);
        GType vips_image_type_get_type (void);

        typedef struct _GData GData;

        typedef struct _GTypeClass GTypeClass;

        typedef struct _GTypeInstance {
            GTypeClass *g_class;
        } GTypeInstance;

        typedef struct _GObject {
            GTypeInstance g_type_instance;
            unsigned int ref_count;
            GData *qdata;
        } GObject;

        typedef struct _GParamSpec {
            GTypeInstance g_type_instance;

            const char* name;
            unsigned int flags;
            GType value_type;
            GType owner_type;

            // private, but cffi in API mode needs these to be able to get the
            // offset of any member
            char* _nick;
            char* _blurb;
            GData* qdata;
            unsigned int ref_count;
            unsigned int param_id;
        } GParamSpec;

        typedef struct _GEnumValue {
            int value;

            const char *value_name;
            const char *value_nick;
        } GEnumValue;

        typedef struct _GEnumClass {
          GTypeClass *g_type_class;

          int minimum;
          int maximum;
          unsigned int n_values;
          GEnumValue *values;
        } GEnumClass;

        void* g_type_class_ref (GType type);

        void g_object_ref (void* object);
        void g_object_unref (void* object);

        void g_object_set_property (GObject* object,
            const char *name, GValue* value);
        void g_object_get_property (GObject* object,
            const char* name, GValue* value);

        typedef struct _VipsObject {
    '''

    # this field changed name in libvips 8.4
    if _at_least(features, 8, 4):
        code += '''
            GObject parent_instance;
        '''
    else:
        code += '''
            GObject parent_object;
        '''

    code += '''
            bool constructed;
            bool static_object;
            void *argument_table;
            char *nickname;
            char *description;
            bool preclose;
            bool close;
            bool postclose;
            size_t local_memory;
        } VipsObject;

        typedef struct _VipsObjectClass VipsObjectClass;

        typedef struct _VipsArgument {
            GParamSpec *pspec;
        } VipsArgument;

        typedef struct _VipsArgumentInstance {
            VipsArgument parent;

            // more
        } VipsArgumentInstance;

        typedef enum _VipsArgumentFlags {
            VIPS_ARGUMENT_NONE = 0,
            VIPS_ARGUMENT_REQUIRED = 1,
            VIPS_ARGUMENT_CONSTRUCT = 2,
            VIPS_ARGUMENT_SET_ONCE = 4,
            VIPS_ARGUMENT_SET_ALWAYS = 8,
            VIPS_ARGUMENT_INPUT = 16,
            VIPS_ARGUMENT_OUTPUT = 32,
            VIPS_ARGUMENT_DEPRECATED = 64,
            VIPS_ARGUMENT_MODIFY = 128
        } VipsArgumentFlags;

        typedef struct _VipsArgumentClass {
            VipsArgument parent;

            VipsObjectClass *object_class;
            VipsArgumentFlags flags;
            int priority;
            unsigned int offset;
        } VipsArgumentClass;

        int vips_object_get_argument (VipsObject* object,
            const char *name, GParamSpec** pspec,
            VipsArgumentClass** argument_class,
            VipsArgumentInstance** argument_instance);

        void vips_object_print_all (void);

        int vips_object_set_from_string (VipsObject* object,
            const char* options);

        const char* vips_object_get_description (VipsObject* object);

        const char* g_param_spec_get_blurb (GParamSpec* pspec);

        typedef struct _VipsImage {
    '''

    # this field changed name in libvips 8.4
    if _at_least(features, 8, 4):
        code += '''
            VipsObject parent_instance;
        '''
    else:
        code += '''
            VipsObject parent_object;
        '''

    code += '''
            // more
        } VipsImage;

        const char* vips_foreign_find_load (const char* name);
        const char* vips_foreign_find_load_buffer (const void* data,
            size_t size);
        const char* vips_foreign_find_save (const char* name);
        const char* vips_foreign_find_save_buffer (const char* suffix);

        VipsImage* vips_image_new_matrix_from_array (int width, int height,
                const double* array, int size);
        VipsImage* vips_image_new_from_memory (const void* data, size_t size,
                int width, int height, int bands, int format);

        VipsImage* vips_image_copy_memory (VipsImage* image);

        GType vips_image_get_typeof (const VipsImage* image,
            const char* name);
        int vips_image_get (const VipsImage* image,
            const char* name, GValue* value_copy);
        void vips_image_set (VipsImage* image,
            const char* name, GValue* value);
        int vips_image_remove (VipsImage* image, const char* name);

        char* vips_filename_get_filename (const char* vips_filename);
        char* vips_filename_get_options (const char* vips_filename);

        VipsImage* vips_image_new_temp_file (const char* format);

        int vips_image_write (VipsImage* image, VipsImage* out);
        void* vips_image_write_to_memory (VipsImage* in, size_t* size_out);

        typedef struct _VipsInterpolate {
            VipsObject parent_object;

            // more
        } VipsInterpolate;

        VipsInterpolate* vips_interpolate_new (const char* name);

        typedef struct _VipsOperation {
            VipsObject parent_instance;

            // more
        } VipsOperation;

        VipsOperation* vips_operation_new (const char* name);

        typedef void* (*VipsArgumentMapFn) (VipsObject* object,
            GParamSpec* pspec,
            VipsArgumentClass* argument_class,
            VipsArgumentInstance* argument_instance,
            void* a, void* b);

        void* vips_argument_map (VipsObject* object,
            VipsArgumentMapFn fn, void* a, void* b);

        VipsOperation* vips_cache_operation_build (VipsOperation* operation);
        void vips_object_unref_outputs (VipsObject* object);

        int vips_operation_get_flags (VipsOperation* operation);

        void vips_cache_set_max (int max);
        void vips_cache_set_max_mem (size_t max_mem);
        void vips_cache_set_max_files (int max_files);
        void vips_cache_set_trace (int trace);

    '''

    if _at_least(features, 8, 5):
        code += '''
            char** vips_image_get_fields (VipsImage* image);
            int vips_image_hasalpha (VipsImage* image);

        '''

    if _at_least(features, 8, 6):
        code += '''
            GType vips_blend_mode_get_type (void);
            void vips_value_set_blob_free (GValue* value,
                void* data, size_t length);

        '''

    # we must only define these in API mode ... in ABI mode we need to call
    # these things earlier
    if features['api']:
        code += '''
            int vips_init (const char* argv0);
            int vips_version (int flag);
        '''

    # ... means inherit from C defines
    code += '#define VIPS_MAJOR_VERSION ...\n'
    code += '#define VIPS_MINOR_VERSION ...\n'
    code += '#define VIPS_MICRO_VERSION ...\n'

    # add contents of features as a comment ... handy for debugging
    for key, value in features.items():
        code += '//%s = %s\n' % (key, value)

    return code


__all__ = [
    'cdefs'
]
