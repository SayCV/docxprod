#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost-pdf-update-numpages
"""

import argparse
import logging
import re
from pathlib import Path as path

import fitz  # pymupdf

from .docxprod_helper import DOCXPROD_ROOT, logger_init

logger = logging.getLogger(__name__)

def get_pdf_numpages(filepath: path) -> int:
    pdf = fitz.open(filepath)
    page_count = pdf.page_count
    pdf.close()
    return page_count

def update_pdf_numpages_to_metadata(filepath: path, page_count: int):
    with open(filepath, "r+", encoding='utf-8') as f:
        metadata = f.read()
        new_metadata = re.sub(r"""numpages: .*""", "numpages: " + str(page_count), metadata)
        f.seek(0)
        f.truncate() # clear content
        f.write(new_metadata)

def main(doc=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Print additional debugging information"
    )
    parser.add_argument(
        '--input',
        '-i',
        type=path,
        help='The path to the input pdf file')
    parser.add_argument(
        '--metadata',
        '-m',
        type=path,
        help='metadata')
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show the verbose output to the terminal')
    args = parser.parse_args()
    logger_init(args)

    try:
        page_count = get_pdf_numpages(args.input)
        logger.info(f"This pdf includes {page_count} pages.")
        if args.metadata:
            update_pdf_numpages_to_metadata(args.metadata, page_count)
            logger.info(f"Updated numpages to {args.metadata} done.")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
