#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdfilter-docx-pagebreak
"""

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
    dp = DocxPagebreak()
    return pf.run_filters([dp.action], doc=doc)


if __name__ == "__main__":
    main()
