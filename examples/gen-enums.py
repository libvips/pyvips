#!/usr/bin/env python

from pyvips import Image, Operation, GValue, Error, \
    ffi, values_for_enum, vips_lib, gobject_lib, \
    type_map, type_name, type_from_name, nickname_find

# This file generates enums.py -- the set of classes giving the permissible
# values for the pyvips enums. Run with something like:
# 
#   ./gen-enums.py > enums.py
#   mv enums.py ../pyvips


def remove_prefix(enum_str):
    prefix = 'Vips'

    if enum_str.startswith(prefix):
        return enum_str[len(prefix):]

    return enum_str


def generate_enums():
    # otherwise we're missing some enums
    vips_lib.vips_token_get_type()
    vips_lib.vips_saveable_get_type()
    vips_lib.vips_image_type_get_type()

    all_enums = []

    def add_enum(gtype, a, b):
        nickname = type_name(gtype)
        all_enums.append(nickname)

        type_map(gtype, add_enum)

        return ffi.NULL

    type_map(type_from_name('GEnum'), add_enum)

    for name in all_enums:
        gtype = type_from_name(name)
        python_name = remove_prefix(name)

        print('class {0}(object):'.format(python_name))

        for value in values_for_enum(gtype):
            python_name = value.replace('-', '_').upper()
            print('    {0} = \'{1}\''.format(python_name, value))

        print('')
        print('')


if __name__ == "__main__":
    generate_enums()
