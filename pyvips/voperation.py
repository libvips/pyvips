from __future__ import division, print_function

import logging

import pyvips
from pyvips import ffi, vips_lib, Error, _to_bytes, _to_string, GValue, \
    type_map, type_from_name, nickname_find, at_least_libvips

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


class Introspect(object):
    """Build introspection data for operations.

    Make an operation, introspect it, and build a structure representing
    everything we know about it.

    """
    __slots__ = ('description', 'flags', 'details',
                 'required_input', 'optional_input',
                 'required_output', 'optional_output',
                 'doc_optional_input', 'doc_optional_output',
                 'member_x', 'method_args')

    def __init__(self, operation_name):
        op = Operation.new_from_name(operation_name)

        self.description = op.get_description()
        self.flags = vips_lib.vips_operation_get_flags(op.pointer)

        # build a list of constructor arg [name, flags] pairs in arg order
        arguments = []

        def add_args(name, flags):
            if (flags & _CONSTRUCT) != 0:
                # libvips uses '-' to separate parts of arg names, but we
                # need '_' for Python
                name = name.replace('-', '_')
                arguments.append([name, flags])

        if at_least_libvips(8, 7):
            p_names = ffi.new('char**[1]')
            p_flags = ffi.new('int*[1]')
            p_n_args = ffi.new('int[1]')
            result = vips_lib.vips_object_get_args(op.vobject,
                                                   p_names, p_flags, p_n_args)
            if result != 0:
                raise Error('unable to get arguments from operation')
            p_names = p_names[0]
            p_flags = p_flags[0]
            n_args = p_n_args[0]

            for i in range(0, n_args):
                add_args(_to_string(p_names[i]), p_flags[i])
        else:
            def add_construct(self, pspec, argument_class,
                              argument_instance, a, b):
                add_args(_to_string(pspec.name), argument_class.flags)
                return ffi.NULL

            cb = ffi.callback('VipsArgumentMapFn', add_construct)
            vips_lib.vips_argument_map(op.vobject, cb, ffi.NULL, ffi.NULL)

        # logger.debug('arguments = %s', self.arguments)

        # build a hash from arg name to detailed arg information
        self.details = {}
        for name, flags in arguments:
            self.details[name] = {
                "name": name,
                "flags": flags,
                "blurb": op.get_blurb(name),
                "type": op.get_typeof(name)
            }

        # lists of arg names by category
        self.required_input = []
        self.optional_input = []
        self.required_output = []
        self.optional_output = []

        # same, but with deprecated args filtered out ... this is the set we
        # show in documentation
        self.doc_optional_input = []
        self.doc_optional_output = []

        for name, flags in arguments:
            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    (flags & _DEPRECATED) == 0):
                self.required_input.append(name)

                # required inputs which we MODIFY are also required outputs
                if (flags & _MODIFY) != 0:
                    self.required_output.append(name)

            if ((flags & _OUTPUT) != 0 and
                    (flags & _REQUIRED) != 0 and
                    (flags & _DEPRECATED) == 0):
                self.required_output.append(name)

            # deprecated optional args get on to the main arg lists, but are
            # filtered from the documented set
            if ((flags & _INPUT) != 0 and
                    (flags & _REQUIRED) == 0):
                self.optional_input.append(name)

                if (flags & _DEPRECATED) == 0:
                    self.doc_optional_input.append(name)

            if ((flags & _OUTPUT) != 0 and
                    (flags & _REQUIRED) == 0):
                self.optional_output.append(name)

                if (flags & _DEPRECATED) == 0:
                    self.doc_optional_output.append(name)

        # find the first required input image arg, if any ... that will be self
        self.member_x = None
        for name in self.required_input:
            details = self.details[name]
            if details['type'] == GValue.image_type:
                self.member_x = name
                break

        # method args are required args, but without the image they are a
        # method on
        if self.member_x is not None:
            self.method_args = list(self.required_input)
            self.method_args.remove(self.member_x)
        else:
            self.method_args = self.required_input

    # a hash mapping operation names to introspection data
    _introspect_cache = {}

    @classmethod
    def get(cls, operation_name):
        if operation_name not in cls._introspect_cache:
            cls._introspect_cache[operation_name] = Introspect(operation_name)

        return cls._introspect_cache[operation_name]


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
    __slots__ = ()

    # cache nickname -> docstring here
    _docstring_cache = {}

    def __init__(self, pointer):
        # logger.debug('Operation.__init__: pointer = %s', pointer)
        super(Operation, self).__init__(pointer)

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

        intro = Introspect.get(operation_name)

        if len(intro.required_input) != len(args):
            raise Error('{0} needs {1} arguments, but {2} given'
                        .format(operation_name,
                                len(intro.required_input),
                                len(args)))

        op = Operation.new_from_name(operation_name)

        # set any string options before any args so they can't be
        # overridden
        string_options = kwargs.pop('string_options', '')
        if not op.set_string(string_options):
            raise Error('unable to call {0}'.format(operation_name))

        # the first image argument is the thing we expand constants to
        # match ... look inside tables for images, since we may be passing
        # an array of images as a single param
        match_image = _find_inside(lambda x: isinstance(x, pyvips.Image),
                                   args)

        logger.debug('VipsOperation.call: match_image = %s', match_image)

        # collect a list of all input references here
        # we can't use a set because set elements are unique under "==", and
        # Python checks memoryview equality with hash functions, not pointer
        # equality
        references = []

        # does a list contain an element using pointer equality
        # we can't use "in" since that uses "==", which means hash equality
        def contains(array, x):
            for y in array:
                if id(x) == id(y):
                    return True
            return False

        def add_reference(x):
            if isinstance(x, pyvips.Image):
                for i in x._references:
                    if not contains(references, i):
                        references.append(i)
            return False

        # set required input args
        for name, value in zip(intro.required_input, args):
            _find_inside(add_reference, value)
            op.set(name, intro.details[name]['flags'], match_image, value)

        # set any optional args
        for name in kwargs:
            if (name not in intro.optional_input and
                    name not in intro.optional_output):
                raise Error('{0} does not support optional argument {1}'
                            .format(operation_name, name))

            value = kwargs[name]
            details = intro.details[name]

            if (details['flags'] & _DEPRECATED) != 0:
                logger.info('%s argument %s is deprecated',
                            operation_name, name)

            _find_inside(add_reference, value)
            op.set(name, details['flags'], match_image, value)

        # build operation
        vop = vips_lib.vips_cache_operation_build(op.pointer)
        if vop == ffi.NULL:
            vips_lib.vips_object_unref_outputs(op.vobject)
            raise Error('unable to call {0}'.format(operation_name))
        op = Operation(vop)

        # attach all input refs to output x
        def set_reference(x):
            if isinstance(x, pyvips.Image):
                x._references.extend(references)
            return False

        # fetch required output args (plus modified input images)
        result = []
        for name in intro.required_output:
            value = op.get(name)
            _find_inside(set_reference, value)
            result.append(value)

        # fetch optional output args
        opts = {}
        for name in intro.optional_output:
            if name in kwargs:
                value = op.get(name)
                _find_inside(set_reference, value)
                opts[name] = value

        if len(opts) > 0:
            result.append(opts)

        vips_lib.vips_object_unref_outputs(op.vobject)

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

        # we cache these to save regeneration
        if operation_name in Operation._docstring_cache:
            return Operation._docstring_cache[operation_name]

        intro = Introspect.get(operation_name)
        if (intro.flags & _OPERATION_DEPRECATED) != 0:
            raise Error('No such operator.',
                        'operator "{0}" is deprecated'.format(operation_name))

        result = intro.description[0].upper() + intro.description[1:] + '.\n\n'
        result += 'Example:\n'

        result += '   ' + ', '.join(intro.required_output) + ' = '
        if intro.member_x is not None:
            result += intro.member_x + '.' + operation_name + '('
        else:
            result += 'pyvips.Image.' + operation_name + '('

        args = []
        args += intro.method_args
        args += [x + '=' + GValue.gtype_to_python(intro.details[x]['type'])
                 for x in intro.doc_optional_input]
        args += [x + '=bool'
                 for x in intro.doc_optional_output]
        result += ", ".join(args) + ')\n'

        def argstr(name):
            details = intro.details[name]
            return (u'    {0} ({1}): {2}\n'.
                    format(name,
                           GValue.gtype_to_python(details['type']),
                           details['blurb']))

        result += '\nReturns:\n'
        for name in intro.required_output:
            result += argstr(name)

        result += '\nArgs:\n'
        if intro.member_x is not None:
            result += argstr(intro.member_x)
        for name in intro.method_args:
            result += argstr(name)

        if len(intro.doc_optional_input) > 0:
            result += '\nKeyword args:\n'
            for name in intro.doc_optional_input:
                result += argstr(name)

        if len(intro.doc_optional_output) > 0:
            result += '\nOther Parameters:\n'
            for name in intro.doc_optional_output:
                result += argstr(name)

        result += '\nRaises:\n    :class:`.Error`\n'

        # add to cache to save building again
        Operation._docstring_cache[operation_name] = result

        return result

    @staticmethod
    def generate_sphinx(operation_name):
        """Make a sphinx-style docstring.

        This is used to generate the off-line docs.

        """

        intro = Introspect.get(operation_name)
        if (intro.flags & _OPERATION_DEPRECATED) != 0:
            raise Error('No such operator.',
                        'operator "{0}" is deprecated'.format(operation_name))

        if intro.member_x is not None:
            result = '.. method:: '
        else:
            result = '.. staticmethod:: '
        args = []
        args += intro.method_args
        args += [x + '=' + GValue.gtype_to_python(intro.details[x]['type'])
                 for x in intro.doc_optional_input]
        args += [x + '=bool'
                 for x in intro.doc_optional_output]
        result += operation_name + '(' + ", ".join(args) + ')\n\n'

        result += intro.description[0].upper() + \
            intro.description[1:] + '.\n\n'

        result += 'Example:\n'
        result += '    '
        if len(intro.required_output) > 0:
            result += ', '.join(intro.required_output) + ' = '
        if intro.member_x is not None:
            result += intro.member_x + "." + operation_name + '('
        else:
            result += 'pyvips.Image.' + operation_name + '('
        args = []
        args += intro.method_args
        args += [x + '=' + GValue.gtype_to_python(intro.details[x]['type'])
                 for x in intro.doc_optional_input]
        result += ', '.join(args)
        result += ')\n\n'

        for name in intro.method_args + intro.doc_optional_input:
            details = intro.details[name]
            result += (':param {0}: {1}\n'.
                       format(name, details['blurb']))
            result += (':type {0}: {1}\n'.
                       format(name, GValue.gtype_to_python(details['type'])))
        for name in intro.doc_optional_output:
            result += (':param {0}: enable output: {1}\n'.
                       format(name, intro.details[name]['blurb']))
            result += (':type {0}: bool\n'.format(name))

        output_types = [GValue.gtype_to_python(intro.details[name]['type'])
                        for name in intro.required_output]
        if len(output_types) == 1:
            output_type = output_types[0]
        else:
            output_type = 'list[' + ', '.join(output_types) + ']'

        if len(intro.doc_optional_output) > 0:
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

        # these names are aliased
        alias = ["crop"]
        alias_gtypes = {}
        for name in alias:
            gtype = pyvips.type_find("VipsOperation", name)
            alias_gtypes[gtype] = name

        # all names we can generate docstrings for
        all_names = []

        def add_name(gtype, a, b):
            if gtype in alias_gtypes:
                name = alias_gtypes[gtype]
            else:
                name = nickname_find(gtype)

            try:
                Operation.generate_sphinx(name)
                all_names.append(name)
            except Error:
                pass

            type_map(gtype, add_name)

            return ffi.NULL

        type_map(type_from_name('VipsOperation'), add_name)

        all_names.sort()

        # remove operations we have to wrap by hand
        exclude = ['scale', 'ifthenelse', 'bandjoin', 'bandrank']
        all_names = [x for x in all_names if x not in exclude]

        # Output summary table
        print('.. class:: pyvips.Image\n')
        print('   .. rubric:: Methods\n')
        print('   .. autosummary::')
        print('      :nosignatures:\n')
        for name in all_names:
            print('      ~{0}'.format(name))
        print()

        # Output docs
        print()
        for name in all_names:
            docstr = Operation.generate_sphinx(name)
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


def cache_get_max():
    """Get the maximum number of operations libvips will cache."""
    return vips_lib.vips_cache_get_max()


def cache_get_size():
    """Get the current size of the operations cache."""
    return vips_lib.vips_cache_get_size()


def cache_get_max_mem():
    """Get the operation cache limit by memory use."""
    return vips_lib.vips_cache_get_max_mem()


def cache_get_max_files():
    """Get the operation cache limit by number of open files."""
    return vips_lib.vips_cache_get_max_files()


def block_untrusted_set(state):
    """Set the block state for all untrusted operations."""
    if at_least_libvips(8, 13):
        vips_lib.vips_block_untrusted_set(state)


def operation_block_set(name, state):
    """Set the block state for a named operation."""
    if at_least_libvips(8, 13):
        vips_lib.vips_operation_block_set(_to_bytes(name), state)


__all__ = [
    'Introspect', 'Operation',
    'cache_set_max', 'cache_set_max_mem', 'cache_set_max_files',
    'cache_set_trace',
    'cache_get_max', 'cache_get_max_mem', 'cache_get_max_files',
    'cache_get_size',
    'block_untrusted_set', 'operation_block_set',
]
