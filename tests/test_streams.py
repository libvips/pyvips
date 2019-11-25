# vim: set fileencoding=utf-8 :

import tempfile

import pyvips
from helpers import JPEG_FILE, temp_filename, skip_if_no


class Mystreami(pyvips.Streamiu):
    def __init__(self, pointer):
        super(Mystreami, self).__init__(pointer)

        # these must be attached before we build the streamiu, see `new`
        self.signal_connect('read', self.read_cb)
        self.signal_connect('seek', self.seek_cb)

    @staticmethod
    def new(name, pipe_mode=False):
        """Make a new input stream from a filename. 

        """

        gtype = pyvips.type_from_name('VipsStreamiu')
        pointer = pyvips.GObject.new_pointer_from_gtype(gtype)
        self = Mystreami(pointer)

        self.name = name
        self.pipe_mode = pipe_mode
        self.loaded_bytes = open(name, 'rb').read()
        self.memory = memoryview(loaded_bytes)
        self.length = len(self.loaded_bytes)
        self.read_point = 0

        return self.build()

    def read_cb(self, buf):
        #print('read: {0} bytes ...'.format(len(buf)))
        p = self.read_point
        bytes_available = self.length - p
        bytes_to_copy = min(bytes_available, len(buf))
        buf[:bytes_to_copy] = self.memory[p:p + bytes_to_copy]
        self.read_point += bytes_to_copy

        return bytes_to_copy

    def seek_cb(self, offset, whence):
        #print('seek: offset = {0}, whence = {1} ...'.format(offset, whence))
        if whence == 0:
            # SEEK_SET
            new_read_point = offset
        elif whence == 1:
            # SEEK_CUR
            new_read_point = self.read_point + offset
        elif whence == 2:
            # SEEK_END
            new_read_point = self.length + offset
        else:
            raise Exception('bad whence {0}'.format(whence))

        self.read_point = max(0, min(self.length, new_read_point))
        #print('   new read_point = {0}'.format(self.read_point))

        if self.pipe_mode:
            return -1
        else:
            return self.read_point


class Mystreamo(pyvips.Streamou):
    def __init__(self, pointer):
        super(Mystreamo, self).__init__(pointer)

        # these must be attached before we build the streamou, see `new`
        self.signal_connect('write', self.write_cb)
        self.signal_connect('finish', self.finish_cb)

    @staticmethod
    def new(name):
        """Make a new output stream from a filename. 

        """

        gtype = pyvips.type_from_name('VipsStreamou')
        pointer = pyvips.GObject.new_pointer_from_gtype(gtype)
        self = Mystreamo(pointer)

        self.name = name
        self.f = open(name, 'wb')

        return self.build()

    def write_cb(self, buf):
        #print('write: {0} bytes ...'.format(len(buf)))

        self.f.write(buf)

        return len(buf)

    def finish_cb(self):
        #print('finish: ...')
        self.f.close()


class TestSignals:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    @skip_if_no('jpegload')
    def test_stream(self):
        streami = pyvips.Streami.new_from_file(JPEG_FILE)
        image = pyvips.Image.new_from_stream(streami, '', access='sequential')
        filename = temp_filename(self.tempdir, '.png')
        streamo = pyvips.Streamo.new_to_file(filename)
        image.write_to_stream(streamo, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE, access='sequential')
        image2 = pyvips.Image.new_from_file(filename, access='sequential')

        assert abs(image - image2).abs().max() < 10

    @skip_if_no('jpegload')
    def test_streamu(self):
        streamiu = Mystreami.new(JPEG_FILE)
        image = pyvips.Image.new_from_stream(streamiu, '', access='sequential')

        filename = temp_filename(self.tempdir, '.jpg')
        streamou = Mystreamo.new(filename)
        image.write_to_stream(streamou, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE)
        image2 = pyvips.Image.new_from_file(filename)

        assert abs(image - image2).abs().max() < 10

    @skip_if_no('jpegload')
    def test_streamu_pipe(self):
        streamiu = Mystreami.new(JPEG_FILE, True)
        image = pyvips.Image.new_from_stream(streamiu, '', access='sequential')

        filename = temp_filename(self.tempdir, '.jpg')
        streamou = Mystreamo.new(filename)
        image.write_to_stream(streamou, '.png')

        image = pyvips.Image.new_from_file(JPEG_FILE)
        image2 = pyvips.Image.new_from_file(filename)

        assert abs(image - image2).abs().max() < 10
