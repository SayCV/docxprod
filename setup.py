import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 0):
    sys.exit("Sorry, Python < 3.0 is not supported")

import re

VERSIONFILE = "docxprod/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

entry_points = {
    'console_scripts': [
        "docxprod-helper = docxprod.docxprod_helper:main",
        "pdfilter-docx-centertext = docxprod.pdfilter_docx_centertext:main",
        "pdfilter-docx-colortext = docxprod.pdfilter_docx_colortext:main",
        "pdfilter-docx-pagebreak = docxprod.pdfilter_docx_pagebreak:main",
        "pdfilter-docx-svg2emf = docxprod.pdfilter_docx_svg2emf:main",
        "pdfilter-docx-update-tabwdith = docxprod.pdfilter_docx_update_tabwdith:main",
        "pdpost-docx-update-fields = docxprod.pdpost_docx_update_fields:main",
        "pdpost-pdf-update-numpages = docxprod.pdpost_pdf_update_numpages:main",
        "pdpost-pdf-update-bookmark = docxprod.pdpost_pdf_update_bookmark:main",
        "pdpost-pdf-update-tocpage = docxprod.pdpost_pdf_update_tocpage:main",
    ],
}

install_requires = [
    "argcomplete >= 1.8.2",
    "colorama >= 0.3.7",
    "panflute >= 2.1.3",
    "pymupdf >= 1.21.1",
    "cssutils >= 2.3.0",
    "colordict >= 1.2.6",
]

setup(
    name="docxprod",
    version=verstr,
    description="docxprod",
    long_description="Please visit `Github <https://github.com/saycv/docxprod>`_ for more information.",
    author="docxprod project developers",
    author_email="",
    url="https://github.com/saycv/docxprod",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    entry_points=entry_points,
    include_package_data=True,
    install_requires=install_requires,
)
