DESCRIPTION = "Script for REMEDY project"
LONG_DESCRIPTION = """"""

DISTNAME = "remedy"
MAINTAINER = "Bianca Pedreschi"
MAINTAINER_EMAIL = "bianca.pedreschi@imtlucca.it"
URL = ""
LICENSE = "The Unlicense"
DOWNLOAD_URL = ""
VERSION = "0.0.1"
PACKAGE_DATA = {}

INSTALL_REQUIRES = [
    "numpy>=1.24.4"
]

PACKAGES = []

CLASSIFIERS = []

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if __name__ == "__main__":
    setup(
        name=DISTNAME,
        author=MAINTAINER,
        author_email=MAINTAINER_EMAIL,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        download_url=DOWNLOAD_URL,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        classifiers=CLASSIFIERS,
    )