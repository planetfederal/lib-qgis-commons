import os
from setuptools import setup

setup(
    name="qgiscommons",
    version="2.0",
    author="Victor Olaya",
    author_email="volaya@boundlessgeo.com",
    description="Common functions and classes to be used in QGIS plugins",    
    license="GPL",
    keywords="qgis",
    url='https://github.com/boundlessgeo/lib-qgis-commons',    
    packages=['qgiscommons2', 'qgiscommons2.gui', 'qgiscommons2.network'],
    package_data = {'qgiscommons2' : ["icons/*"] },
    include_package_data=True
)
