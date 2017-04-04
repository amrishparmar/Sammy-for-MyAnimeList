from time import sleep
from multiprocessing.pool import ThreadPool

import click


def loading_animation(msg):
    for c in "|/-\\":
        click.echo("\r{}...{}".format(msg, c), nl=False)
        sleep(0.07)


def threaded_action(action, msg="Loading", *args, **kwds):
    pool = ThreadPool(processes=1)

    async_result = pool.apply_async(action, args=args, kwds=kwds)

    while not async_result.ready():
        loading_animation(msg)

    click.echo("\r{}...Done".format(msg))
    click.echo()

    return async_result.get()

