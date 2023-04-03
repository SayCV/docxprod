#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
- pdpost_docx_update_fields
"""

import argparse
import logging
import time
from pathlib import Path as path

import win32com.client

from .docxprod_helper import (DOCXPROD_ROOT, logger_init)

logger = logging.getLogger(__name__)

def update_fields(filepath: path):
    extension = filepath.suffix
    acceptable_ext = ['.doc','.docx']
    #word = comtypes.client.CreateObject('Word.Application') # opens the word application
    word = win32com.client.Dispatch('Word.Application')

    if extension not in acceptable_ext:
        logger.error(f'Error: Incorrect Filetype {extension}')
    else:    
        doc = word.Documents.Open(str(filepath)) # opens the specified file
        #doc.SelectAll()
        for field in doc.Fields:
            if field.Type != 37 and field.Type != 88:
                response = field.UpdateSource()
                logger.info(f'Success with {field.Code()}')
                time.sleep(1)
            #break
        response = doc.Fields.Update() # updates field, returns 0 if successful ->  Invaildate action
        if response != 0:
            logger.error(f'Error with {filepath} on field at Index {str(response)} ')
        if response == 0:
            #doc.Save(NoPrompt=True, OriginalFormat=1)
            doc.Save()
            logger.info(f'Success with {filepath}')
        doc.Close()
    word.Quit()

def main(doc=None):

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="Print additional debugging information"
    )
    parser.add_argument(
        '--output',
        '-o',
        type=path,
        help='The path for the output docx file')
    parser.add_argument(
        '--input',
        '-i',
        type=path,
        help='The path to the input docx file')
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Show the verbose output to the terminal')
    args = parser.parse_args()
    logger_init(args)

    try:
        update_fields(args.input)
    except Exception as e:
        print(e)
    logger.info(f"Updated fields done")

if __name__ == '__main__':
    main()
