#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pagebreak.docx.py
"""

from pathlib import Path as path

PDFILTERS_PY_ROOT = path(__file__).resolve().parent

def main():
    print(PDFILTERS_PY_ROOT)


if __name__ == "__main__":
    main()
