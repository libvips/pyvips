from __future__ import division, print_function

import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes, _to_string, GValue, \
    type_map, type_from_name, nickname_find

logger = logging.getLogger(__name__)

# values for VipsArgumentFlags
_REQUIRED = 1
_CONSTRUCT = 2
_SET_ONCE = 4
_SET_ALWAYS = 8
_INPUT = 16
_OUTPUT = 32
_DEPRECATED = 64
_MODIFY = 128

# for VipsOperationFlags
_OPERATION_DEPRECATED = 8


# search an array with a predicate, recursing into subarrays as we see them
# used to find the match_image for an operation
def _find_inside(pred, thing):
    if pred(thing):
        return thing

    if isinstance(thing, list) or isinstance(thing, tuple):
        for x in thing:
            result = _find_inside(pred, x)

            if result is not None:
                return result

    return None


class Operation(pyvips.VipsObject):
    """Call libvips operations.

    This class wraps the libvips VipsOperation class.

    """

    # cache nickname -> docstring here
    _docstring_cache = {}

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Operation, self).__init__(pointer)
        self.object = ffi.cast('VipsObject*', pointer)

    @staticmethod
    def new_from_name(operation_name):
        vop = vips_lib.vips_operation_new(_to_bytes(operation_name))
        if vop == ffi.NULL:
            raise Error('no such operation {0}'.format(operation_name))
        return Operation(vop)

    def set(self, name, flags, match_image, value):
        # if the object wants an image and we have a constant, _imageize it
        #
        # if the object wants an image array, _imageize any constants in the
        # array
        if match_image:
            gtype = self.get_typeof(name)

            if gtype == pyvips.GValue.image_type:
                value = pyvips.Image._imageize(match_image, value)
            elif gtype == pyvips.GValue.array_image_type:
                value = [pyvips.Image._imageize(match_image, x)
                         for x in value]

        # MODIFY args need to be copied before they are set
        if (flags & _MODIFY) != 0:
            # logger.debug('copying MODIFY arg %s', name)
            # make sure we have a unique copy
            value = value.copy().copy_memory()

        super(Operation, self).set(name, value)

    def get_flags(self):
        return vips_lib.vips_operation_get_flags(self.pointer)

    # this is slow ... call as little as possible
    def get_args(self):
        args = []

        def add_construct(self, pspec, argument_class,
                          argument_instance, a, b):
            flags = argument_class.flags
            if (flags & _CONSTRUCT) != 0:
                name = _to_string(pspec.name)

                # libvips uses '-' to separate parts of arg names, but we
                # need '_' for Python
                name = name.replace('-', '_')

                args.append([name, flags])

            return ffi.NULL

        cb = ffi.callback('VipsArgumentMapFn', add_construct)
        vips_lib.vips_argument_map(self.object, cb, ffi.NULL, ffi.NULL)

        return args

    @staticmethod
    def call(operation_name, *args, **kwargs):
        """Call a libvips operation.

        Use this method to call any libvips operation. For example::

            black_image = pyvips.Operation.call('black', 10, 10)

        See the Introduction for notes on how this works.

        """

        logger.debug('VipsOperation.call: operation_name = %s', operation_name)
        # logger.debug('VipsOperation.call: args = %s, kwargs =%s',
        #              args, kwargs)

        # pull out the special string_options kwarg
        string_options = kwargs.pop('string_options', '')

        logger.debug('VipsOperation.call: string_options = %s', string_options)

        op = Operation.new_from_name(operation_name)

        arguments = op.get_args()
        # logger.debug('arguments = %s', arguments)

        # make a thing to quickly get flags from an arg name
        flags_from_name = {}

        # count required input args
        n_required = 0

        for name, flags in arguments:
            flags_from_name[name] = flags

            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    (flags & _DEPRECATED) == 0):
                n_required += 1

        if n_required != len(args):
            raise Error('unable to call {0}: {1} arguments given, '
                        'but {2} required'.format(operation_name, len(args),
                                                  n_required))

        # the first image argument is the thing we expand constants to
        # match ... look inside tables for images, since we may be passing
        # an array of image as a single param
        match_image = _find_inside(lambda x:
                                   isinstance(x, pyvips.Image),
                                   args)

        logger.debug('VipsOperation.call: match_image = %s', match_image)

        # set any string options before any args so they can't be
        # overridden
        if not op.set_string(string_options):
            raise Error('unable to call {0}'.format(operation_name))

        # set required and optional args
        n = 0
        for name, flags in arguments:
            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    (flags & _DEPRECATED) == 0):
                op.set(name, flags, match_image, args[n])
                n += 1

        for name, value in kwargs.items():
            if name not in flags_from_name:
                raise Error('{0} does not support argument '
                            '{1}'.format(operation_name, name))

            op.set(name, flags_from_name[name], match_image, value)

        # build operation
        vop = vips_lib.vips_cache_operation_build(op.pointer)
        if vop == ffi.NULL:
            raise Error('unable to call {0}'.format(operation_name))
        op = Operation(vop)

        # find all input images and gather up all the references they hold
        references = []

        def add_reference(x):
            if isinstance(x, pyvips.Image):
                # += won't work on non-local references
                for i in x._references:
                    references.append(i)

            return False

        _find_inside(add_reference, args)
        for key, value in kwargs.items():
            _find_inside(add_reference, value)

        # fetch required output args, plus modified input images
        result = []
        for name, flags in arguments:
            if ((flags & _OUTPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    (flags & _DEPRECATED) == 0):
                result.append(op.get(name))

            if (flags & _INPUT) != 0 and (flags & _MODIFY) != 0:
                result.append(op.get(name))

        # fetch optional output args
        opts = {}
        for name, value in kwargs.items():
            flags = flags_from_name[name]

            if ((flags & _OUTPUT) != 0 and
                    (flags & _REQUIRED) == 0 and
                    (flags & _DEPRECATED) == 0):
                opts[name] = op.get(name)

        vips_lib.vips_object_unref_outputs(op.object)

        if len(opts) > 0:
            result.append(opts)

        # all output images need all input references
        def set_reference(x):
            if isinstance(x, pyvips.Image):
                x._references += references

            return False

        _find_inside(set_reference, result)

        if len(result) == 0:
            result = None
        elif len(result) == 1:
            result = result[0]

        logger.debug('VipsOperation.call: result = %s', result)

        return result

    @staticmethod
    def generate_docstring(operation_name):
        """Make a google-style docstring.

        This is used to generate help() output.

        """

        if operation_name in Operation._docstring_cache:
            return Operation._docstring_cache[operation_name]

        op = Operation.new_from_name(operation_name)
        if (op.get_flags() & _OPERATION_DEPRECATED) != 0:
            raise Error('No such operator.',
                        'operator "{0}" is deprecated'.format(operation_name))

        # we are only interested in non-deprecated args
        args = [[name, flags] for name, flags in op.get_args()
                if not flags & _DEPRECATED]

        # find the first required input image arg, if any ... that will be self
        member_x = None
        for name, flags in args:
            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    op.get_typeof(name) == GValue.image_type):
                member_x = name
                break

        required_input = [name for name, flags in args
                          if (flags & _INPUT) != 0 and
                          (flags & _REQUIRED) != 0 and
                          name != member_x]

        optional_input = [name for name, flags in args
                          if (flags & _INPUT) != 0 and
                             (flags & _REQUIRED) == 0]

        required_output = [name for name, flags in args
                           if ((flags & _OUTPUT) != 0 and
                               (flags & _REQUIRED) != 0) or
                              ((flags & _INPUT) != 0 and
                               (flags & _REQUIRED) != 0 and
                               (flags & _MODIFY) != 0)]

        optional_output = [name for name, flags in args
                           if (flags & _OUTPUT) != 0 and
                              (flags & _REQUIRED) == 0]

        description = op.get_description()
        result = description[0].upper() + description[1:] + ".\n\n"
        result += "Example:\n"

        result += "   " + ", ".join(required_output) + " = "
        if member_x is not None:
            result += member_x + "." + operation_name + "("
        else:
            result += "pyvips.Image." + operation_name + "("

        result += ", ".join(required_input)
        if len(optional_input) > 0 and len(required_input) > 0:
            result += ", "
        result += ", ".join([x + " = " +
                             GValue.gtype_to_python(op.get_typeof(x))
                             for x in optional_input])
        result += ")\n"

        def argstr(name):
            return (u'    {0} ({1}): {2}\n'.
                    format(name,
                           GValue.gtype_to_python(op.get_typeof(name)),
                           op.get_blurb(name)))

        result += "\nReturns:\n"
        for name in required_output:
            result += argstr(name)

        names = []
        if member_x is not None:
            names += [member_x]
        names += required_input

        result += "\nArgs:\n"
        for name in names:
            result += argstr(name)

        if len(optional_input) > 0:
            result += "\nKeyword args:\n"
            for name in optional_input:
                result += argstr(name)

        if len(optional_output) > 0:
            result += "\nOther Parameters:\n"
            for name in optional_output:
                result += argstr(name)

        result += "\nRaises:\n    :class:`.Error`\n"

        # add to cache to save building again
        Operation._docstring_cache[operation_name] = result

        return result

    @staticmethod
    def generate_sphinx(operation_name):
        """Make a sphinx-style docstring.

        This is used to generate the off-line docs.

        """

        op = Operation.new_from_name(operation_name)
        if (op.get_flags() & _OPERATION_DEPRECATED) != 0:
            raise Error('No such operator.',
                        'operator "{0}" is deprecated'.format(operation_name))

        # we are only interested in non-deprecated args
        args = [[name, flags] for name, flags in op.get_args()
                if not flags & _DEPRECATED]

        # find the first required input image arg, if any ... that will be self
        member_x = None
        for name, flags in args:
            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    op.get_typeof(name) == GValue.image_type):
                member_x = name
                break

        required_input = [name for name, flags in args
                          if (flags & _INPUT) != 0 and
                          (flags & _REQUIRED) != 0 and
                          name != member_x]

        optional_input = [name for name, flags in args
                          if (flags & _INPUT) != 0 and
                             (flags & _REQUIRED) == 0]

        required_output = [name for name, flags in args
                           if ((flags & _OUTPUT) != 0 and
                               (flags & _REQUIRED) != 0) or
                              ((flags & _INPUT) != 0 and
                               (flags & _REQUIRED) != 0 and
                               (flags & _MODIFY) != 0)]

        optional_output = [name for name, flags in args
                           if (flags & _OUTPUT) != 0 and
                              (flags & _REQUIRED) == 0]

        if member_x is not None:
            result = '.. method:: '
        else:
            result = '.. staticmethod:: '
        args = []
        args += required_input
        args += [x + ' = ' + GValue.gtype_to_python(op.get_typeof(x))
                 for x in optional_input]
        args += [x + ' = bool'
                 for x in optional_output]
        result += operation_name + '(' + ", ".join(args) + ')\n\n'

        description = op.get_description()
        result += description[0].upper() + description[1:] + '.\n\n'

        result += 'Example:\n'
        result += '    ' + ', '.join(required_output) + ' = '
        if member_x is not None:
            result += member_x + "." + operation_name + '('
        else:
            result += 'pyvips.Image.' + operation_name + '('
        result += ', '.join(required_input)
        if len(optional_input) > 0 and len(required_input) > 0:
            result += ', '
        result += ', '.join([x + ' = ' +
                             GValue.gtype_to_python(op.get_typeof(x))
                             for x in optional_input])
        result += ')\n\n'

        for name in required_input + optional_input:
            result += (':param {0} {1}: {2}\n'.
                       format(GValue.gtype_to_python(op.get_typeof(name)),
                              name,
                              op.get_blurb(name)))
        for name in optional_output:
            result += (':param bool {0}: enable output: {1}\n'.
                       format(name,
                              op.get_blurb(name)))

        output_types = [GValue.gtype_to_python(op.get_typeof(name))
                        for name in required_output]
        if len(output_types) == 1:
            output_type = output_types[0]
        else:
            output_type = 'list[' + ', '.join(output_types) + ']'

        if len(optional_output) > 0:
            output_types += ['Dict[str, mixed]']
            output_type += ' or list[' + ', '.join(output_types) + ']'

        result += ':rtype: ' + output_type + '\n'
        result += ':raises Error:\n'

        return result

    @staticmethod
    def generate_sphinx_all():
        """Generate sphinx documentation.

        This generates a .rst file for all auto-generated image methods. Use it
        to regenerate the docs with something like::

            $ python -c \
"import pyvips; pyvips.Operation.generate_sphinx_all()" > x

        And copy-paste the file contents into doc/vimage.rst in the appropriate
        place.

        """

        # generate list of all nicknames we can generate docstrings for

        all_nicknames = []

        def add_nickname(gtype, a, b):
            nickname = nickname_find(gtype)
            try:
                Operation.generate_sphinx(nickname)
                all_nicknames.append(nickname)
            except Error:
                pass

            type_map(gtype, add_nickname)

            return ffi.NULL

        type_map(type_from_name('VipsOperation'), add_nickname)

        all_nicknames.sort()

        # remove operations we have to wrap by hand

        exclude = ['scale', 'ifthenelse', 'bandjoin', 'bandrank']
        all_nicknames = [x for x in all_nicknames if x not in exclude]

        # Output summary table
        print('.. class:: pyvips.Image\n')
        print('   .. rubric:: Methods\n')
        print('   .. autosummary::')
        print('      :nosignatures:\n')
        for nickname in all_nicknames:
            print('      ~{0}'.format(nickname))
        print()

        # Output docs
        print()
        for nickname in all_nicknames:
            docstr = Operation.generate_sphinx(nickname)
            docstr = docstr.replace('\n', '\n      ')
            print('   ' + docstr)


def cache_set_max(mx):
    """Set the maximum number of operations libvips will cache."""
    vips_lib.vips_cache_set_max(mx)


def cache_set_max_mem(mx):
    """Limit the operation cache by memory use."""
    vips_lib.vips_cache_set_max_mem(mx)


def cache_set_max_files(mx):
    """Limit the operation cache by number of open files."""
    vips_lib.vips_cache_set_max_files(mx)


def cache_set_trace(trace):
    """Turn on libvips cache tracing."""
    vips_lib.vips_cache_set_trace(trace)


__all__ = [
    'Operation',
    'cache_set_max', 'cache_set_max_mem', 'cache_set_max_files',
    'cache_set_trace'
]
