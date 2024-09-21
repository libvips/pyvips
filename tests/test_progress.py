# vim: set fileencoding=utf-8 :

import pytest

import pyvips


class TestProgress:
    def test_progress(self):
        seen_preeval = False
        seen_eval = False
        seen_posteval = False

        def preeval_cb(image, progress):
            nonlocal seen_preeval
            seen_preeval = True

        def eval_cb(image, progress):
            nonlocal seen_eval
            seen_eval = True

        def posteval_cb(image, progress):
            nonlocal seen_posteval
            seen_posteval = True

        image = pyvips.Image.black(1, 100000)
        image.set_progress(True)
        image.signal_connect('preeval', preeval_cb)
        image.signal_connect('eval', eval_cb)
        image.signal_connect('posteval', posteval_cb)
        image.avg()

        assert seen_preeval
        assert seen_eval
        assert seen_posteval

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
        image.avg()

    def test_progress_kill(self):
        def preeval_cb(image, progress):
            pass

        def eval_cb(image, progress):
            image.set_kill(True)

        def posteval_cb(image, progress):
            pass

        # has to be very tall to ensure the kill has enough threadpool loops
        # to work
        image = pyvips.Image.black(1, 1000000)
        image.set_progress(True)
        image.signal_connect('preeval', preeval_cb)
        image.signal_connect('eval', eval_cb)
        image.signal_connect('posteval', posteval_cb)

        with pytest.raises(Exception):
            image.copy_memory()
