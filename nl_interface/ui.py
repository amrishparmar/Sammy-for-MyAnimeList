from time import sleep
from multiprocessing.pool import ThreadPool

import click


def loading_animation(msg):
    """Print out one rotation of a spinning bar loading animation
    
    :param msg: A string, the message to display
    """
    for c in "|/-\\":
        click.echo("\r{}...{}".format(msg, c), nl=False)
        sleep(0.07)


def threaded_action(action, msg="Loading", *args, **kwds):
    """Perform a potentially long-running action while displaying a loading animation
    
    :param action: A function to perform
    :param msg: A string, the message to display while action is running
    :param args: A tuple, arguments to pass to the action function
    :param kwds: A dictionary, keyword arguments to pass to the action function
    :return: The return value of action function
    """
    tp = ThreadPool(processes=1)

    action_result = tp.apply_async(action, args=args, kwds=kwds)

    while not action_result.ready():
        loading_animation(msg)

    click.echo("\r{}...Finished".format(msg))

    return action_result.get()
