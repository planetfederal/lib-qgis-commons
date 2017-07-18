import os
from setuptools import setup

setup(
    name="qgiscommons",
    version="0.1.5",
    author="Victor Olaya",
    author_email="volaya@boundlessgeo.com",
    description="Common functions and classes to be used in QGIS plugins",    
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    license="GPL",
    keywords="qgis",
    url='https://github.com/boundlessgeo/lib-qgis-commons',
    download_url = 'https://github.com/boundlessgeo/lib-qgis-commons/archive/0.1.tar.gz',    
    packages=['qgiscommons', 'qgiscommons.gui', 'qgiscommons.network'],
    package_data = {'qgiscommons' : ["icons/*"] },
    include_package_data=True
)
