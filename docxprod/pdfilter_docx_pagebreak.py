#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdfilter-docx-pagebreak
"""

import pandocxnos
import panflute as pf


class DocxPagebreak(object):
    pagebreak = pf.RawBlock(
        "<w:p><w:r><w:br w:type=\"page\" /></w:r></w:p>", format="openxml")
    sectionbreak = pf.RawBlock("<w:p><w:pPr><w:sectPr><w:type w:val=\"nextPage\" /></w:sectPr></w:pPr></w:p>",
                               format="openxml")

    def action(self, elem, doc):
        if type(elem) == pf.Div and "style" in elem.attributes and 'page-break-after' in elem.attributes["style"]:
            if (doc.format == "docx"):
                pf.debug(f"Processing page break at index {elem.index}")
                elem = self.pagebreak
        return elem


def main(doc=None):
    PANDOCVERSION = pandocxnos.init(None, doc)
    if pandocxnos.version(PANDOCVERSION) <= pandocxnos.version('1.0'):
        pf.debug(f"Not support for Pandoc version: {PANDOCVERSION}")
        return pf.run_filters([])
    dp = DocxPagebreak()
    return pf.run_filters([dp.action], doc=doc)


if __name__ == "__main__":
    main()
