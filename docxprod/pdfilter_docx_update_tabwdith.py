#!/usr/bin/env python3

"""
A pandoc filter that allows to explicitly set the column widths for tables.
Column width can get passed to the table as an attribute in its caption:
    Table: This is the caption {#tbl:tab1 colwidth=".2 .2 .6"}

- pdfilter-docx-update-tabwdith
"""

import os
import sys
import panflute as pf

DOCX_TABLE_FULL_WIDTH_DEFAULT = 9576

class DocxTableUpdateWidth(object):

    def __init__(self):
        self.enable_table_fullwidth = True
        env_enable = os.environ.get('enable_table_fullwidth')
        if env_enable:
            self.enable_table_fullwidth = False if env_enable.lower() in 'false' else True
        pf.debug(f':: Used enable_table_fullwidth: {self.enable_table_fullwidth}')

    def action(self, elem, doc):
        if self.enable_table_fullwidth and doc.format == "docx":
            if isinstance(elem, pf.Table):
                pf.debug(f"Processing update table width at index {elem.index}")
                for idx, colspec in enumerate(elem.colspec):
                    colalign = colspec[0]
                    colwidth = colspec[1]
                    if isinstance(colwidth, str) and "ColWidthDefault" in colwidth:
                        elem.colspec[idx] = (colalign, 1.0/elem.cols)
                    elif isinstance(colwidth, float):
                        pass
                return elem

def main(doc=None):
    dp = DocxTableUpdateWidth()
    return pf.run_filters([dp.action], doc=doc)

if __name__ == '__main__':
    main()
