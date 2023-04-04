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

from docxprod.docxprod_helper import DOCXPROD_ROOT, logger_init
from docxprod.pdpost_pdf_update_bookmark import update_toc_bookmark

logger = logging.getLogger(__name__)

each_toc_tpl = r'''
<a style="display: flex; margin-bottom: 6px; text-decoration: none; color: inherit" href="${ this.href }">
    <div>${ this.title }</div>
    <div style="margin: 0 4px; flex: 1; border-bottom: 2px dotted black"></div>
    <div>${ this.page }</div>
</a>
'''
def norm_name(name):
    """Replace hex parts of the fontname."""
    while "#" in name:  # any hexadecimals in the name?
        p = name.find("#")
        c = int(name[p + 1 : p + 3], 16)
        name = name.replace(name[p : p + 3], chr(c))
    if name.find("+") == 6:  # only if '+' at position 5
        return True, name[7:]
    return False, name

def get_fontnames(doc, item):
    """Return a list of fontnames for an item of 'page.get_fonts()'.
    There may be more than one alternative e.g. for Type0 fonts.
    """
    fontname = item[3]
    subset, fontname = norm_name(fontname)
    names = [fontname]
    xref = item[0]
    text = doc.xref_object(item[0])
    font = ""
    descendents = ""
    t, temp = doc.xref_get_key(xref, "BaseFont")
    if t == "name":
        _, font = norm_name(temp[1:])
        names.append(font)
    t, temp = doc.xref_get_key(xref, "DescendantFonts")
    if t != "array":  # no DescendantFonts - done
        return subset, tuple(set(names))
    temp = temp[1:-1]  # remove array brackets

    # DescendantFonts is either one xref or one embedded PDF dictionary
    if temp.endswith(">>"):  # embedded dictionary!
        temp_list = temp.split("/")  # split at name separator
        try:
            p0 = temp_list.index("BaseFont")
        except:  # no fontname provided - done
            return subset, tuple(set(names))
        p0 += 1  # next item is the fontname
        font = temp_list[p0]
        _, font = norm_name(font)
        names.append(font)
        return subset, tuple(set(names))
    # DescendantFonts given as xref
    nxref = int(temp.replace("0 R", ""))  # get xref of DescendantFonts
    t, temp = doc.xref_get_key(nxref, "BaseFont")
    if t == "name":  # fontname, append it
        _, font = norm_name(temp[1:])
        names.append(font)
    return subset, tuple(set(names))


def make_msg(font):
    flags = font.flags
    msg = ["%i glyphs" % font.glyph_count, "size %i" % len(font.buffer)]
    if flags["mono"] == 1:
        msg.append("mono")
    if flags["serif"]:
        msg.append("serifed")
    if flags["italic"]:
        msg.append("italic")
    if flags["bold"]:
        msg.append("bold")
    msg = ", ".join(msg)
    return msg

def get_font_list(pdf) -> list:
    font_list = set()
    for i in range(len(pdf)):
        for f in pdf.get_page_fonts(i, full=True):
            msg = ""
            subset, fontname = get_fontnames(pdf, f)

            if f[1] == "n/a":
                msg = "Not embedded!"
            else:
                extr = pdf.extract_font(f[0])
                font = fitz.Font(fontbuffer=extr[-1])
                msg = make_msg(font)

            if subset:
                msg += ", subset font"
            font_list.add((fontname, msg))

    font_list = list(font_list)
    font_list.sort(key=lambda x: x[0])
    return font_list


def update_toc_page(args: argparse.Namespace, toc: list):

    pdf = fitz.open(args.input)
    fonts = get_font_list(pdf)
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
                #logger.debug(
                #    f"{available_width}, {font.text_length(toc_entry.title + str(page_num), fontsize=fontsize)}, {one_dot_width} x {one_dot_num}, {font.text_length(text, fontsize=fontsize)}")

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
        '--markdown-file',
        type=path,
        default=None,
        help='Parse toc contents from the markdown file')
    parser.add_argument(
        '--shift-heading-level-by',
        type=int,
        metavar='NUMBER',
        default='1',
        help='Provided the min level of title')
    parser.add_argument(
        '--toc-depth',
        type=int,
        metavar='NUMBER',
        default='3',
        help='Provided the max level of title')
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
