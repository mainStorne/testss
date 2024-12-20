import logging


def handler(event, ctx):
    logging.info(event)
    return {'event': event, 'ctx': ctx, 'statusCode': 200}
