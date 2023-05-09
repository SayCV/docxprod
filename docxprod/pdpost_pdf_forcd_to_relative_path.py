#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost-pdf-forcd-to-relative-path
"""

import argparse
import logging
import os
import re
import traceback
from pathlib import Path as path
from string import Template

import fitz  # pymupdf
from fitzutils import ToCEntry
import rtoml

from docxprod.docxprod_helper import DOCXPROD_ROOT, logger_init


logger = logging.getLogger(__name__)


def forcd_to_relative_path(args: argparse.Namespace):
    data = rtoml.load(args.metadata)
    if not data:
        return
    relinks = data.get('relinks').get('files')

    doc = fitz.open(args.input)
    for page in doc:
        lnks = page.get_links()
        for link_in_page in lnks:
            if not 'file' in link_in_page:
                continue
            print(link_in_page)
            for link in relinks:
                if not isinstance(link, list):
                    continue
                src_link: str = link_in_page['file']
                dst_link: str = link[0] if link[1] == "" else link[1]
                if src_link.endswith(link[0]):
                    link_in_page['file'] = ""
                    link_in_page['kind'] = fitz.LINK_URI
                    link_in_page['uri'] = dst_link
                    page.update_link(link_in_page)
                    logger.debug(f"Succeeded to do {src_link} -> {dst_link}.")
    doc.save(args.output)


def main(doc=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Print additional debugging information"
    )
    parser.add_argument(
        '--input',
        '-i',
        type=path,
        default="example.pdf",
        help='The path to the input pdf file')
    parser.add_argument(
        '--output',
        '-o',
        type=path,
        help='The path to the output pdf file')
    parser.add_argument(
        '--metadata',
        type=path,
        default="metadata.relink.toml",
        help='Provided the search text')
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show the verbose output to the terminal')
    args = parser.parse_args()
    logger_init(args)

    if args.input is None:
        parser.print_help()
        exit(1)
    if not path(args.input).exists():
        logger.info(f"Input file non-exist -> {args.input}.")
        exit(1)
    if args.output is None:
        args.output = path(args.input).with_suffix(".rel.pdf")
    if not path(args.metadata).exists():
        logger.info(f"Metadata file non-exist -> {args.metadata}.")
        exit(1)

    try:
        forcd_to_relative_path(args)
        logger.info(f"Forcd to relative path done.")
    except Exception as e:
        # logging.error(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
