#!/usr/bin/python3

import sys
import xml.etree.ElementTree as ET

from pyvips import ffi, values_for_enum, values_for_flag, \
    vips_lib, type_map, type_name, type_from_name

# This file generates enums.py -- the set of classes giving the permissible
# values for the pyvips enums/flags. Run with something like:
#
#   ./gen-enums.py ~/GIT/libvips/build/libvips/Vips-8.0.gir > enums.py
#   mv enums.py ../pyvips

# The GIR file
root = ET.parse(sys.argv[1]).getroot()
namespace = {
    "goi": "http://www.gtk.org/introspection/core/1.0"
}

# find all the enumerations/flags and make a dict for them
xml_enums = {}
for node in root.findall("goi:namespace/goi:enumeration", namespace):
    xml_enums[node.get('name')] = node

xml_flags = {}
for node in root.findall("goi:namespace/goi:bitfield", namespace):
    xml_flags[node.get('name')] = node


def remove_prefix(enum_str):
    prefix = 'Vips'

    if enum_str.startswith(prefix):
        return enum_str[len(prefix):]

    return enum_str


def generate_enums():
    all_nicknames = []

    def add_nickname(gtype, a, b):
        nickname = type_name(gtype)
        all_nicknames.append(nickname)

        type_map(gtype, add_nickname)

        return ffi.NULL

    type_map(type_from_name('GEnum'), add_nickname)

    for name in all_nicknames:
        gtype = type_from_name(name)
        python_name = remove_prefix(name)
        if python_name not in xml_enums:
            continue

        node = xml_enums[python_name]
        values = values_for_enum(gtype)
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
        for value in values:
            python_name = value.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            member_doc = member.find("goi:doc", namespace)
            if member_doc is not None:
                text = member_doc.text
                print(f'    {python_name.upper()} (str): {text}')
                print('')
        print('    """')
        print('')

        for value in values:
            python_name = value.replace('-', '_').upper()
            print(f'    {python_name} = \'{value}\'')

def generate_flags():
    all_nicknames = []

    def add_nickname(gtype, a, b):
        nickname = type_name(gtype)
        all_nicknames.append(nickname)

        type_map(gtype, add_nickname)

        return ffi.NULL

    type_map(type_from_name('GFlags'), add_nickname)

    # Filter internal flags
    filter = ['VipsForeignFlags']
    all_nicknames = [name for name in all_nicknames if name not in filter]

    for name in all_nicknames:
        gtype = type_from_name(name)
        python_name = remove_prefix(name)
        if python_name not in xml_flags:
            continue

        node = xml_flags[python_name]
        values = values_for_flag(gtype)
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
        for value in values:
            python_name = value.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            member_doc = member.find("goi:doc", namespace)
            if member_doc is not None:
                text = member_doc.text
                print(f'    {python_name.upper()} (int): {text}')
                print('')
        print('    """')
        print('')

        for value in values:
            python_name = value.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            print(f'    {python_name.upper()} = {member.get("value")}')


if __name__ == "__main__":
    # otherwise we're missing some enums
    vips_lib.vips_token_get_type()
    vips_lib.vips_saveable_get_type()
    vips_lib.vips_image_type_get_type()

    print('# libvips enums -- this file is generated automatically')
    print('# flake8: noqa: E501')  # ignore line too long error
    generate_enums()
    generate_flags()
