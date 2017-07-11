import os
from setuptools import setup

def data_files():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "qgiscommons", "icons")
    files = []
    for f in os.listdir(path):
        files.append("qgiscommons/icons/" + f)
    return [("", files)]

setup(
    name="qgiscommons",
    version="0.1",
    author="Victor Olaya",
    author_email="volaya@boundlessgeo.com",
    description="Common functions and classes to be used in QGIS plugins",    
    # Full list of classifiers can be found at:
    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
    ],
    license="GPL",
    keywords="qgis",
    url='https://github.com/boundlessgeo/lib-qgis-commons',
    download_url = 'https://github.com/boundlessgeo/lib-qgis-commons/archive/0.1.tar.gz',    
    packages=['qgiscommons', 'qgiscommons.gui', 'qgiscommons.network'],
    data_files = data_files()
)
