import logging


def setup(cfg=None):
    logging.basicConfig(
        level=logging.INFO,
        # format='%(name)s - %(message)s'
        format='%(message)s'
    )


def get(name=None):
    return logging.getLogger(name)
