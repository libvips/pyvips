#!/usr/bin/python3

import sys
import xml.etree.ElementTree as ET

from pyvips import ffi, values_for_enum, vips_lib, \
    type_map, type_name, type_from_name

# This file generates enums.py -- the set of classes giving the permissible
# values for the pyvips enums. Run with something like:
#
#   ./gen-enums.py ~/GIT/libvips/libvips/Vips-8.0.gir > enums.py
#   mv enums.py ../pyvips

# The GIR file
root = ET.parse(sys.argv[1]).getroot()
namespace = {
    "goi": "http://www.gtk.org/introspection/core/1.0"
}

# find all the enumerations and make a dict for them
xml_enums = {}
for node in root.findall("goi:namespace/goi:enumeration", namespace):
    xml_enums[node.get('name')] = node


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
        if python_name not in xml_enums:
            continue

        node = xml_enums[python_name]
        enum_doc = node.find("goi:doc", namespace)

        print('')
        print('')
        print(f'class {python_name}(object):')
        print(f'    """{python_name}.')
        if enum_doc is not None:
            print('')
            print(f'{enum_doc.text}')
        print('')
        print('Attributes:')
        print('')
        for value in values_for_enum(gtype):
            python_name = value.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            member_doc = member.find("goi:doc", namespace)
            if member_doc is not None:
                text = member_doc.text
                print(f'    {python_name.upper()} (str): {text}')
                print('')
        print('    """')
        print('')

        for value in values_for_enum(gtype):
            python_name = value.replace('-', '_').upper()
            print(f'    {python_name} = \'{value}\'')


if __name__ == "__main__":
    print('# libvips enums -- this file is generated automatically')
    print('# flake8: noqa: E501')  # ignore line too long error
    generate_enums()
