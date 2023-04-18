#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdfilter-docx-colortext
"""

from functools import partial
from colorutils import *
import panflute as pf

def stringify(element, newlines=True):
    def attach_str(e, doc, answer):
        if hasattr(e, 'text'):
            ans = e.text
        elif isinstance(e, (pf.Space, pf.SoftBreak)):
            ans = ' '
        elif isinstance(e, pf.LineBreak):
            ans = '\n'
        elif isinstance(e, (pf.Para, )) and newlines:
            ans = '\n\n'
        elif type(e) == pf.Citation:
            ans = ''
        else:
            ans = ''

        # Add quotes around the contents of Quoted()
        if type(e.parent) == pf.Quoted:
            if e.index == 0:
                ans = '"' + ans
            if e.index == len(e.container) - 1:
                ans += '"'

        answer.append(ans)

    answer = []
    f = partial(attach_str, answer=answer)
    element.walk(f)
    return ''.join(answer)

class DocxColortext(object):
    def colortext(self, color_hex, text): return r'''
<w:r w:rsidRPr="008B16E0">
    <w:rPr>
        <w:color w:val="''' + color_hex + r'''" />
        <w:lang w:eastAsia="zh-CN" />
    </w:rPr>
    <w:t>''' + text + r'''</w:t>
</w:r>
'''

    def action(self, elem, doc):
        if type(elem) == pf.Span and "style" in elem.attributes and 'color' in elem.attributes["style"]:
            if (doc.format == "docx"):
                style = elem.attributes["style"]
                f1 = style.split(':')
                color = None
                if len(f1) > 1 and f1[0] in 'color':
                    color = f1[1]

                try:
                    color_hex = rgb_to_hex(web_colors[color])
                except KeyError as e:
                    #pf.debug(f"KeyError: {e}")
                    try:
                        r, g, b = eval(color.lower().lstrip("rgb"))
                        color_hex = rgb_to_hex((r, g, b))
                    except (ValueError, SyntaxError) as e:
                        #pf.debug(f"ValueError: {e}")
                        color_hex = color
                color_hex = color_hex.lstrip("#")

                _elem = []
                text_list = stringify(elem).split('\n')
                for text in text_list:
                    _elem.append(self.colortext(color_hex, text))
                pf.debug(f"Processing {color_hex} text at line {elem.index}: {pf.stringify(elem)}")
                elem = pf.RawInline('<w:r><w:br /></w:r>'.join(_elem), format="openxml")
        return elem


def main(doc=None):
    dp = DocxColortext()
    return pf.run_filters([dp.action], doc=doc)


if __name__ == "__main__":
    main()
