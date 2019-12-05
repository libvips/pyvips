from __future__ import division

import logging

import pyvips
from pyvips import vips_lib

logger = logging.getLogger(__name__)


class Streamiu(pyvips.Streami):
    """An input stream you can connect action signals to to implement
    behaviour.

    """

    def __init__(self):
        """Make a new user input stream.

        Attach handlers to the `::read` and `::seek` signals to implement
        other behavours. Subclass this to add state.

        You can pass this stream to (for example) :meth:`new_from_stream`.

        """

        super(Streamiu, self).__init__(vips_lib.vips_streamiu_new())


__all__ = ['Streamiu']
