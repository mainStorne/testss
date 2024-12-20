import logging


def handler(event, ctx):
    logging.info(event)
    return {'isAuthorized': False}
