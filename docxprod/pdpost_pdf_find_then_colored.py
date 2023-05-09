#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost-pdf-find-then-colored
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

from docxprod.docxprod_helper import DOCXPROD_ROOT, logger_init


logger = logging.getLogger(__name__)


def find_then_colored_text(args: argparse.Namespace, text: str, color_name: str, font_name: str):
    color = (1, 0, 0)
    if color_name == "green":
        color = (0, 1, 0)
    elif color_name == "blue":
        color = (0, 0, 1)
    doc = fitz.open(args.input)
    page = doc[0]
    rl = page.search_for(text)
    #assert len(rl) == 1
    logger.info(f"Found {len(rl)} positions.")
    
    font = None
    for i in range(len(rl)):
        clip = rl[i]
        # extract text info now - before the redacting removes it.
        blocks = page.get_text("dict", clip=clip)["blocks"]
        span = blocks[0]["lines"][0]["spans"][0]
        #assert span["text"] == text
        #logger.info(f'Changing {span["text"]}.')

        # remove text
        page.add_redact_annot(clip)
        page.apply_redactions()

        # re-insert same text - different color
        # this must be known somehow - or simply try some font else
        if font is None:
            font = fitz.Font(font_name)
        tw = fitz.TextWriter(page.rect, color=color)
        # text insertion must use the original insertion poin and font size.
        # if not original font, then some fontsize adjustments will probably be required:
        # check bbox.width against textlength computed with new font
        tw.append(span["origin"], text, font=font, fontsize=span["size"])
        tw.write_text(page)
    doc.ez_save(args.output)


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
        '--output',
        '-o',
        type=path,
        help='The path to the output pdf file')
    parser.add_argument(
        '--text',
        help='Provided the search text')
    parser.add_argument(
        '--color',
        default='red',
        help='Provided the new color')
    parser.add_argument(
        '--font',
        default='courier',
        choices=['courier', 'courier-oblique', 'courier-bold', 'courier-boldoblique',
                 'helvetica', 'helvetica-oblique', 'helvetica-bold', 'helvetica-boldoblique',
                 'times-roman', 'times-italic', 'times-bold', 'times-bolditalic',
                 'symbol', 'zapfdingbats',
                 'helv', 'heit', 'hebo', 'hebi', 'cour',
                 'coit', 'cobo', 'cobi',
                 'tiro', 'tibo', 'tiit', 'tibi',
                 'symb', 'zadb'],
        help='Provided the new color')
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
        args.output = path(args.input).with_suffix(".ftc.pdf")

    try:
        find_then_colored_text(args, args.text, args.color, args.font)
        logger.info(f"Find then colored text done.")
    except Exception as e:
        # logging.error(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
