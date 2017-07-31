# wrapper for libvips

# Our cvlasses need to refer to each other ... make them go via this
# module-level global which we update at the end with the real classes
class_index = {
    'Image': 'banana',
    'Operation': 'apple',
    'GValue': 'kumquat'
}

from base import *
from gvalue import GValue
from gobject import GObject
from vobject import VipsObject
from voperation import Operation
from vimage import Image

class_index['Image'] = Image
class_index['Operation'] = Operation
class_index['GValue'] = GValue

__all__ = ['Image', 'Operation', 'GValue']
