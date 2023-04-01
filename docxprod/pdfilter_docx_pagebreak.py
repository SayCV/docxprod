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
    toc = pf.RawBlock(r"""
<w:sdt>
    <w:sdtContent xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
        <w:p>
            <w:r>
                <w:fldChar w:fldCharType="begin" w:dirty="true" />
                <w:instrText xml:space="preserve">TOC \o "1-3" \h \z \u</w:instrText>
                <w:fldChar w:fldCharType="separate" />
                <w:fldChar w:fldCharType="end" />
            </w:r>
        </w:p>
    </w:sdtContent>
</w:sdt>
""", format="openxml")

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
