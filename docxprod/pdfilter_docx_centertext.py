#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- centertext.docx.py
"""

import panflute as pf


class DocxCentertext(object):
    def centertext(self, str): return pf.RawBlock(r"""
<w:p>
    <w:pPr>
        <w:pStyle w:val="FirstParagraph" />
        <w:jc w:val="center" />
    </w:pPr>
    <w:r>
        <w:t>""" + str + r"""</w:t>
    </w:r>
</w:p>
""", format="openxml")

    def centertext_bold(self, str): return pf.RawBlock(r"""
<w:p>
    <w:pPr>
        <w:pStyle w:val="FirstParagraph" />
        <w:jc w:val="center" />
    </w:pPr>
    <w:r>
        <w:rPr>
            <w:b />
        </w:rPr>
        <w:t>""" + str + r"""</w:t>
    </w:r>
</w:p>
""", format="openxml")

    def action(self, elem, doc):
        if type(elem) == pf.Div and "style" in elem.attributes and 'text-align:center' in elem.attributes["style"]:
            if (doc.format == "docx"):
                pf.debug(f"Processing center text at line {elem.index}: {pf.stringify(elem)}")
                if 'font-weight:bold' in elem.attributes["style"]:
                    elem = self.centertext_bold(pf.stringify(elem))
                else:
                    elem = self.centertext(pf.stringify(elem))
        return elem


def main(doc=None):
    dp = DocxCentertext()
    return pf.run_filters([dp.action], doc=doc)


if __name__ == "__main__":
    main()
