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
        "pdfilter-docx-pagebreak = docxprod.pdfilter_docx_pagebreak:main",
        "pdfilter-docx-svg2emf = docxprod.pdfilter_docx_svg2emf:main",
        "pdfilter-docx-tab-update-wdith = docxprod.pdfilter_docx_tab_update_wdith:main",
    ],
}

install_requires = [
    "argcomplete >= 1.8.2",
    "colorama >= 0.3.7",
    "panflute >= 2.1.3",
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