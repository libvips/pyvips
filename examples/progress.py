#!/usr/bin/python3

import pyvips


def progress_print(name, progress):
    print('{}:'.format(name))
    print('   run = {}'.format(progress.run))
    print('   eta = {}'.format(progress.eta))
    print('   tpels = {}'.format(progress.tpels))
    print('   npels = {}'.format(progress.npels))
    print('   percent = {}'.format(progress.percent))


def preeval_cb(image, progress):
    progress_print('preeval', progress)


def eval_cb(image, progress):
    progress_print('eval', progress)

    # you can kill computation if necessary
    if progress.percent > 50:
        image.set_kill(True)


def posteval_cb(image, progress):
    progress_print('posteval', progress)


image = pyvips.Image.black(1, 500)
image.set_progress(True)
image.signal_connect('preeval', preeval_cb)
image.signal_connect('eval', eval_cb)
image.signal_connect('posteval', posteval_cb)
image.avg()
