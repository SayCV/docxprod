#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pagebreak.docx.py
"""

import os
import panflute as pf


class DocxSvg2emf(object):

    def action(self, elem, doc):
        docx_support_svg = os.environ.get('docx_support_svg')
        if (doc.format == "docx"):
            if isinstance(elem, pf.Image):
                fn = elem.url
                if fn.endswith(".svg"):
                    if docx_support_svg:
                        pf.debug(f"docx_support_svg: {docx_support_svg}")
                        return elem
                    elem.url = os.path.splitext(fn)[0]+'.emf'
                    pf.debug(
                        "[inline] changed .svg file to {}".format(elem.url))
        return elem


def main(doc=None):
    dp = DocxSvg2emf()
    return pf.run_filters([dp.action], doc=doc)


if __name__ == "__main__":
    main()
