#!/usr/bin/python3

import pyvips


def progress_print(name, progress):
    print(f'{name}:'.format(name))
    print(f'   run = {progress.run}')
    print(f'   eta = {progress.eta}')
    print(f'   tpels = {progress.tpels}')
    print(f'   npels = {progress.npels}')
    print(f'   percent = {progress.percent}')


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
