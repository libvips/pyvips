from __future__ import division

import logging

import pyvips
from pyvips import vips_lib

logger = logging.getLogger(__name__)


class Streamou(pyvips.Streamo):
    """An output stream you can connect action signals to to implement
    behaviour.

    """

    def __init__(self):
        """Make a new stream from a file descriptor (a small integer).

        Attach handlers to the `"write"` and `"finish"` signals to implement
        other behavours. Subclass this to add state.

        You can pass this stream to (for example) :meth:`write_to_stream`.

        """

        super(Streamou, self).__init__(vips_lib.vips_streamou_new())


__all__ = ['Streamou']
