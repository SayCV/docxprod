#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- docxprod-helper
"""

import functools
import logging
from pathlib import Path as path

DOCXPROD_ROOT = path(__file__).resolve().parent.as_posix()

def logger_init(args=None):

    # Setup logging for displaying background information to the user.
    logging.basicConfig(
        style="{", format="[{levelname:<7}] {message}", level=logging.INFO
    )
    # Add a custom status level for logging.
    logging.addLevelName(25, "STATUS")
    logging.Logger.status = functools.partialmethod(logging.Logger.log, 25)
    logging.status = functools.partial(logging.log, 25)

    # Change logging level if `--debug` was supplied.
    if args and args.debug:
        logging.getLogger("").setLevel(logging.DEBUG)

def main():
    print(DOCXPROD_ROOT)


if __name__ == "__main__":
    main()
