#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost-pdf-update-tocpage
"""

import argparse
import logging
import re
import traceback
from pathlib import Path as path
from string import Template

import fitz  # pymupdf
from fitzutils import ToCEntry

from .docxprod_helper import DOCXPROD_ROOT, logger_init
from .pdpost_pdf_update_bookmark import update_toc_bookmark

logger = logging.getLogger(__name__)

each_toc_tpl = r'''
<a style="display: flex; margin-bottom: 6px; text-decoration: none; color: inherit" href="${ this.href }">
    <div>${ this.title }</div>
    <div style="margin: 0 4px; flex: 1; border-bottom: 2px dotted black"></div>
    <div>${ this.page }</div>
</a>
'''


def generated_toc_page_html(toc) -> str:
    toc_page_title = '\u76ee\u5f55'
    toc_page_head = f'<html>\n<body>\n<div class="print-toc">\n<h1>{toc_page_title}</h1>'
    toc_page_tail = '</div>\n</body>\n</html>'

    toc_list = []
    for _toc in toc:
        t = Template(each_toc_tpl)
        d = {
            "this.href": None,
            "this.title": _toc[1],
            "this.page": _toc[2],
        }
        each_toc_content = t.substitute(d)
        toc_list.append(each_toc_content)
    toc_page_body = '\n'.join(toc_list)
    return toc_page_head + toc_page_body + toc_page_tail


def update_toc_page(args: argparse.Namespace, toc: list):

    pdf = fitz.open(args.input)
    fonts = pdf.get_page_fonts(0)
    logger.debug(fonts)

    if toc:
        logger.info(f"Convert toc bookmark to toc page.")
        # page_width, page_height = fitz.paper_size("A4") # 595, 842
        page_width, page_height = pdf[0].rect.width, pdf[0].rect.height
        logger.info(f"Page Width = {page_width}, Page Height = {page_height}")
        page: fitz.Page = pdf.new_page(
            pno=0, width=page_width, height=page_height)

        hMargin = 20
        vMargin = 20
        available_width = page_width - 2 * hMargin

        fontname = 'HT'
        fontfile = r"C:/Windows/Fonts/simhei.ttf"
        page.insert_font(fontname=fontname, fontfile=fontfile,
                         fontbuffer=None, set_simple=False)
        font = fitz.Font(fontname=fontname, fontfile=fontfile, fontbuffer=None)
        logger.debug(page.get_fonts())

        text = '\u76ee\u5f55'
        fontsize = 28
        #text_width = page.get_text_length(text, fontname=fontname)
        text_width = font.text_length(text, fontsize=fontsize)
        px = (page_width - text_width) / 2
        py = vMargin + vMargin
        page.insert_text((px, py), text, fontname=fontname, fontsize=fontsize, color=(0, 0, 0, 1), fill=None, render_mode=0,
                         border_width=1, rotate=0, morph=None, overlay=True)

        fontsize = 12
        row_space = 32
        px = hMargin
        py += row_space
        row_space = 22
        for line, _toc in enumerate(toc):
            toc_entry = ToCEntry(_toc[0], _toc[1], _toc[2], _toc[3])
            level = toc_entry.level
            page_num = toc_entry.pagenum
            vpos = toc_entry.vpos

            fontsize = 12 if level < 2 else 12 #10.5
            row_space = 10 if level < 2 else 10
            toc_entry.title = ' ' * 4 * (level - 1) + toc_entry.title
            text = f"{toc_entry.title}{page_num}"
            #text_width = fitz.get_text_length(text, fontname=fontname)
            #one_dot_width = fitz.get_text_length('.', fontname=fontname)
            text_width = font.text_length(text, fontsize=fontsize)
            one_dot_width = font.text_length('.', fontsize=fontsize)
            if text_width < available_width:
                one_dot_num = int((available_width - text_width)/one_dot_width)
                text = toc_entry.title + '.' * one_dot_num
                text = f"{toc_entry.title}{'.' * one_dot_num}{page_num}"
                logger.debug(
                    f"{available_width}, {font.text_length(toc_entry.title + str(page_num), fontsize=fontsize)}, {one_dot_width} x {one_dot_num}, {font.text_length(text, fontsize=fontsize)}")

            # https://github.com/pymupdf/PyMuPDF/issues/648
            tl = font.text_length(text, fontsize=fontsize)
            start = fitz.Point(px, py)
            line_height = fontsize * 1.3
            r = fitz.Rect(start, start.x + tl, start.y + line_height)
            link = {"kind": fitz.LINK_GOTO, "from": r,
                    'page': page_num, 'to': vpos['to'], 'zoom': 0.0}
            page.insert_link(link)
            page.insert_text(r.bl, text, fontname=fontname, fontsize=fontsize, color=(0, 0, 0, 1), fill=None, render_mode=0,
                            border_width=1, rotate=0, morph=None, overlay=True)

            py += 1 * line_height
            #py += row_space

    pdf_in_file: path = args.input
    pdf_out_file: path = pdf_in_file.parent / \
        (pdf_in_file.stem + '_toc_page.pdf')
    pdf.save(pdf_out_file)
    pdf.close()


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
        '--level',
        type=int,
        default='4',
        help='Provided the level of title')
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show the verbose output to the terminal')
    args = parser.parse_args()
    logger_init(args)

    try:
        args.pdf_bookmark_css = f'{DOCXPROD_ROOT}/data/pdf_bookmark_default.css'
        toc = update_toc_bookmark(args, enable_update_pdf=False)
        update_toc_page(args, toc)
        logger.info(f"Updated toc page to pdf done.")
    except Exception as e:
        # logging.error(e)
        traceback.print_exc()


if __name__ == '__main__':
    main()
