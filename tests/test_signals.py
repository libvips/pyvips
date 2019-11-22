# vim: set fileencoding=utf-8 :

import os
import pytest
import tempfile

import pyvips
from helpers import JPEG_FILE, temp_filename, skip_if_no


class TestSignals:
    @classmethod
    def setup_class(cls):
        cls.tempdir = tempfile.mkdtemp()

    def test_progress(self):
        # py27 reques this pattern for non-local modification
        notes = {}

        def preeval_cb(image, progress):
            notes['seen_preeval'] = True

        def eval_cb(image, progress):
            notes['seen_eval'] = True

        def posteval_cb(image, progress):
            notes['seen_posteval'] = True

        image = pyvips.Image.black(10, 1000)
        image.set_progress(True)
        image.signal_connect('preeval', preeval_cb)
        image.signal_connect('eval', eval_cb)
        image.signal_connect('posteval', posteval_cb)
        image.copy_memory()

        assert notes['seen_preeval']
        assert notes['seen_eval']
        assert notes['seen_posteval']

    def test_progress_fields(self):
        def preeval_cb(image, progress):
            assert progress.run == 0
            assert progress.eta == 0
            assert progress.percent == 0
            assert progress.tpels == 10000
            assert progress.npels == 0

        def eval_cb(image, progress):
            pass

        def posteval_cb(image, progress):
            assert progress.percent == 100
            assert progress.tpels == 10000
            assert progress.npels == 10000

        image = pyvips.Image.black(10, 1000)
        image.set_progress(True)
        image.signal_connect('preeval', preeval_cb)
        image.signal_connect('eval', eval_cb)
        image.signal_connect('posteval', posteval_cb)
        image.copy_memory()

    @pytest.mark.skip(reason='this works in my code, but segvs in pytest')
    def test_progress_kill(self):
        def preeval_cb(image, progress):
            pass

        def eval_cb(image, progress):
            image.set_kill(True)

        def posteval_cb(image, progress):
            pass

        image = pyvips.Image.black(10, 1000)
        image.set_progress(True)
        image.signal_connect('preeval', preeval_cb)
        image.signal_connect('eval', eval_cb)
        image.signal_connect('posteval', posteval_cb)

        with pytest.raises(Exception):
            image.copy_memory()

    @skip_if_no('jpegload')
    def test_stream(self):
        streami = pyvips.Streami.new_from_file(JPEG_FILE)
        image = pyvips.Image.new_from_stream(streami, '', access='sequential')
        filename = temp_filename(self.tempdir, '.jpg')
        streamo = pyvips.Streamo.new_to_file(filename)
        image.write_to_stream(streamo, '.jpg')

        image = pyvips.Image.new_from_file(JPEG_FILE)
        image2 = pyvips.Image.new_from_file(filename)

        assert abs(image.avg() - image2.avg()) < 0.1

