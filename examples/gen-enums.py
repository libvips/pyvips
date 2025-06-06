#!/usr/bin/env python3

import sys
import xml.etree.ElementTree as ET

from pyvips import ffi, enum_dict, flags_dict, \
    type_map, type_name, type_from_name

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


def rewrite_references(string):
    """Rewrite a gi-docgen references to RST style.

    gi-docgen references look like this:

        [func@version]
        [class@Image]
        [func@Image.bandjoin]
        [meth@Image.add]
        [ctor@Image.new_from_file]
        [enum@SdfShape]
        [enum@Vips.SdfShape.CIRCLE]

    we look for the approximate patterns and rewrite in RST style, so:

        :meth:`.version`
        :class:`.Image`
        :meth:`.Image.bandjoin`
        :meth:`.Image.new_from_file`
        :class:`.enums.SdfShape`
        :class:`.enums.SdfShape.CIRCLE`
    """

    import re
    while True:
        match = re.search(r"\[(.*?)@(.*?)\]", string)
        if not match:
            break

        before = string[0:match.span(0)[0]]
        type = match[1]
        target = match[2]
        after = string[match.span(0)[1]:]

        if type in ["ctor", "meth", "method", "func"]:
            python_type = "meth"
        elif type in ["class", "enum", "flags"]:
            python_type = "class"
        else:
            raise Exception(f'type "{type}" is unknown')

        match = re.match("Vips.(.*)", target)
        if match:
            target = match[1]

        if type == "enum":
            target = f"enums.{target}"

        string = f"{before}:{python_type}:`.{target}`{after}"

    return string


def generate_enums():
    all_nicknames = []

    def add_nickname(gtype, a, b):
        nickname = type_name(gtype)
        all_nicknames.append(nickname)

        type_map(gtype, add_nickname)

        return ffi.NULL

    type_map(type_from_name('GEnum'), add_nickname)

    # Filter internal enums
    blacklist = ['VipsDemandStyle']
    all_nicknames = [name for name in all_nicknames if name not in blacklist]

    for name in all_nicknames:
        gtype = type_from_name(name)
        python_name = remove_prefix(name)
        if python_name not in xml_enums:
            continue

        node = xml_enums[python_name]
        values = enum_dict(gtype)
        enum_doc = node.find("goi:doc", namespace)

        print('')
        print('')
        print(f'class {python_name}(object):')
        print(f'    """{python_name}.')
        if enum_doc is not None:
            print('')
            print(f'{rewrite_references(enum_doc.text)}')
        print('')
        print('Attributes:')
        print('')
        for key, value in values.items():
            python_name = key.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            member_doc = member.find("goi:doc", namespace)
            if member_doc is not None:
                text = rewrite_references(member_doc.text)
                print(f'    {python_name.upper()} (str): {text}')
                print('')
        print('    """')
        print('')

        for key, value in values.items():
            python_name = key.replace('-', '_').upper()
            print(f'    {python_name} = \'{key}\'')


def generate_flags():
    all_nicknames = []

    def add_nickname(gtype, a, b):
        nickname = type_name(gtype)
        all_nicknames.append(nickname)

        type_map(gtype, add_nickname)

        return ffi.NULL

    type_map(type_from_name('GFlags'), add_nickname)

    # Filter internal flags
    blacklist = ['VipsForeignFlags']
    all_nicknames = [name for name in all_nicknames if name not in blacklist]

    for name in all_nicknames:
        gtype = type_from_name(name)
        python_name = remove_prefix(name)
        if python_name not in xml_flags:
            continue

        node = xml_flags[python_name]
        values = flags_dict(gtype)
        enum_doc = node.find("goi:doc", namespace)

        print('')
        print('')
        print(f'class {python_name}(object):')
        print(f'    """{python_name}.')
        if enum_doc is not None:
            print('')
            print(f'{rewrite_references(enum_doc.text)}')
        print('')
        print('Attributes:')
        print('')
        for key, value in values.items():
            python_name = key.replace('-', '_')
            member = node.find(f"goi:member[@name='{python_name}']", namespace)
            member_doc = member.find("goi:doc", namespace)
            if member_doc is not None:
                text = member_doc.text
                print(f'    {python_name.upper()} (int): '
                      f'{rewrite_references(text)}')
                print('')
        print('    """')
        print('')

        for key, value in values.items():
            python_name = key.replace('-', '_').upper()
            print(f'    {python_name} = {value}')


if __name__ == "__main__":
    print('# libvips enums -- this file is generated automatically')
    print('# flake8: noqa: E501')  # ignore line too long error
    generate_enums()
    generate_flags()
