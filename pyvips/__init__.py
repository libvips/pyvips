# wrapper for libvips

# Our classes need to refer to each other ... make them go via this
# package-level global which we update at the end with references to the real
# classes
package_index = {
    'Image': 'banana',
    'Operation': 'apple',
    'GValue': 'kumquat'
}

from base import *
from enums import *
from gvalue import GValue
from gobject import GObject
from vobject import VipsObject
from voperation import Operation
from vimage import Image
from vinterpolate import Interpolate

package_index['Image'] = Image
package_index['Operation'] = Operation
package_index['GValue'] = GValue

__all__ = ['Error', 'Image', 'Operation', 'GValue']
