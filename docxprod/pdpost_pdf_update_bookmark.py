#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost-pdf-update-bookmark
"""

import argparse
import logging
import re
import traceback

import cssutils
import fitz  # pymupdf
from pathlib import Path as path

from docxprod.docxprod_helper import (DOCXPROD_ROOT, logger_init)

logger = logging.getLogger(__name__)

def parse_css(filepath: path) -> dict:
    with open(filepath, "rb", encoding=None) as f:
        css = f.read()
    sheet = cssutils.parseString(css)
    css_dict = {}
    for rule in sheet:
        selector = rule.selectorText
        #styles = rule.style.cssText
        inner_dict = {}
        for property in rule.style:
            inner_dict[property.name] = property.value
        css_dict[selector] = inner_dict
    return css_dict

def parse_toc(args: argparse.Namespace, css_dict: dict, enable_update_pdf=False) -> list:
    re_font_size = r'(\d+)pt'
    re_head_title = r'h(\d+)'

    enable_main_title = args.enable_main_title
    pdf = fitz.open(args.input)
    toc: list = pdf.get_toc(simple=False)
    if toc:
        logger.info(f"The pdf has included toc.")
        return toc

    for page_num, page in enumerate(pdf, 1):
        text_page = page.get_textpage()
        text_page_dict = text_page.extractDICT()
        blocks = text_page_dict['blocks']

        for one_block in blocks:
            context = one_block['lines'][0]['spans'][0]
            logger.debug(context)
            if context['flags'] == 4:
                for key, values in css_dict.items():
                    pattern = re.compile(re_head_title)
                    match_obj = pattern.match(key)
                    if match_obj:  # get selector named hxxx
                        bmk_level = int(match_obj.group(1))
                        if 'font-size' in values and 'font-family' in values:  # only match font-size and font-family
                            pattern = re.compile(re_font_size)
                            # only support pt for font-size
                            match_obj = pattern.match(values['font-size'])
                            # logger.debug(int(context['size']), round(context['size']))
                            if match_obj and int(match_obj.group(1)) == round(context['size']):
                                line_local = context['bbox'][1]
                                point = fitz.Point(0, float(line_local))
                                if not enable_main_title and bmk_level != args.level:
                                    logger.debug('continue...')
                                    continue
                                elif not enable_main_title:
                                    enable_main_title = True
                                toc.append([bmk_level - args.level + 1, context['text'], page_num, {
                                           'kind': fitz.LINK_GOTO, 'to': point, 'collapse': 1}])

    logger.debug(toc)
    toclen = len(toc)
    page_count = pdf.page_count
    t0 = toc[0]
    for i in list(range(toclen - 1)):
        t1 = toc[i]
        t2 = toc[i + 1]
        if not -1 <= t1[2] <= page_count:
            raise ValueError("row %i: page number out of range" % i)
        if (type(t2) not in (list, tuple)) or len(t2) not in (3, 4):
            raise ValueError("bad row %i" % (i + 1))
        if (type(t2[0]) is not int) or t2[0] < 1:
            raise ValueError("bad hierarchy level in row %i" % (i + 1))
        if t2[0] > t1[0] + 1:
            raise ValueError("bad hierarchy level in row %i" % (i + 1))

    if enable_update_pdf:
        pdf.set_toc(toc)
        pdf_in_file: path = args.input
        pdf_out_file: path = pdf_in_file.parent / (pdf_in_file.stem + '_new.pdf')
        pdf.save(pdf_out_file)
    pdf.close()

    return toc

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
        '--pdf-bookmark-css',
        type=path,
        default=f'{DOCXPROD_ROOT}/data/pdf_bookmark_default.css',
        help='Provided the pdf bookmark css file')
    parser.add_argument(
        '--level',
        type=int,
        default='2',
        help='Provided the level of title')
    parser.add_argument(
        '--enable-main-title',
        action='store_true',
        help='Enabled the main title')
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show the verbose output to the terminal')
    args = parser.parse_args()
    logger_init(args)

    try:
        css_dict = parse_css(args.pdf_bookmark_css)
        toc = parse_toc(args, css_dict, enable_update_pdf=True)
        if True and toc:
            toc_file: path = args.input.with_suffix('.toc')
            toc_str = []
            for _toc in toc:
                toc_str.append(f"{_toc[0]},{_toc[1]},{_toc[2]},{_toc[3]}")
            toc_file.write_text('\n'.join(toc_str))
        logger.info(f"Updated toc to pdf done.")
    except Exception as e:
        #logging.error(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
