import codecs
import os
import re

import setuptools
# from distutils.core import setup
from distutils.extension import Extension

import numpy as np
from Cython.Build import cythonize

current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.join(current_dir, "package")
print(current_dir)
try:
    import imagecodecs
    import imagecodecs._imagecodecs
    imagecodecs_string = imagecodecs.__name__
except ImportError:
    imagecodecs_string = 'imagecodecs-lite>=2019.4.20'

extensions = [
    Extension('PartSegCore.distance_in_structure.euclidean_cython',
              sources=["package/PartSegCore/distance_in_structure/euclidean_cython.pyx"],
              include_dirs=[np.get_include()] + [os.path.join(package_dir, "PartSegCore", "distance_in_structure")],
              language='c++', extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"]),
    Extension('PartSegCore.distance_in_structure.path_sprawl_cython',
              sources=["package/PartSegCore/distance_in_structure/path_sprawl_cython.pyx"],
              include_dirs=[np.get_include()] + [os.path.join(package_dir, "PartSegCore", "distance_in_structure")],
              language='c++', extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"]),
    Extension('PartSegCore.distance_in_structure.sprawl_utils',
              sources=["package/PartSegCore/distance_in_structure/sprawl_utils.pyx"],
              include_dirs=[np.get_include()] + [os.path.join(package_dir, "PartSegCore", "distance_in_structure")],
              language='c++', extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"]),
    Extension('PartSegCore.distance_in_structure.fuzzy_distance',
              sources=["package/PartSegCore/distance_in_structure/fuzzy_distance.pyx"],
              include_dirs=[np.get_include()] + [os.path.join(package_dir, "PartSegCore", "distance_in_structure")],
              language='c++', extra_compile_args=["-std=c++11"], extra_link_args=["-std=c++11"]),
    Extension("PartSegCore.color_image.color_image", ["package/PartSegCore/color_image/color_image.pyx"],
              include_dirs=[np.get_include()],
              extra_compile_args=['-std=c++11'],
              language='c++',
              ),
    Extension("PartSegCore.multiscale_opening.mso_bind", ["package/PartSegCore/multiscale_opening/mso_bind.pyx"],
              include_dirs=[np.get_include()],
              extra_compile_args=['-std=c++11', '-Wall'],
              language='c++',
              # undef_macros=["NDEBUG"],
              # define_macros=[("DEBUG", None)]
              )
]


def read(*parts):
    with codecs.open(os.path.join(current_dir, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def readme():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    reg = re.compile(r'(!\[[^]]*\])\((images/[^)]*)\)')
    reg2 = re.compile(r'PartSeg-lastest')
    with open(os.path.join(this_directory, 'Readme.md')) as f:
        text = f.read()
        text = reg.sub(r'\1(https://raw.githubusercontent.com/4DNucleome/PartSeg/master/\2)', text)
        text = reg2.sub(f"PartSeg-{find_version('package', 'PartSeg', '__init__.py')}", text)
        return text


try:
    import PySide2
    qt_string = PySide2.__name__
except ImportError:
    qt_string = "PyQt5>=5.10.1"


setuptools.setup(
    ext_modules=cythonize(extensions),
    name="PartSeg",
    version=find_version("package", "PartSeg", "__init__.py"),
    author="Grzegorz Bokota",
    author_email="g.bokota@cent.uw.edu.pl",
    description="PartSeg is python GUI for bio imaging analysis",
    url="https://4dnucleome.cent.uw.edu.pl/PartSeg/",
    packages=setuptools.find_packages('./package'),
    package_dir={'': 'package'},
    include_package_data=True,
    long_description=readme(),
    long_description_content_type='text/markdown',
    install_requires=['numpy>=1.16.0', "tifffile>=2019.7.26", "czifile>=2019.4.20", "oiffile>=2019.1.1",
                      imagecodecs_string, 'appdirs>=1.4.3', 'SimpleITK>=1.1.0', 'scipy>=0.19.1', 'QtPy>=1.3.1',
                      'sentry_sdk==0.13.1', qt_string, 'six>=1.11.0', 'h5py>=2.7.1', 'packaging>=17.1',
                      'pandas>=0.22.0', 'sympy>=1.1.1', 'Cython>=0.29.13', 'openpyxl>=2.4.9', 'xlrd>=1.1.0',
                      'PartSegData==0.9.4', "defusedxml>=0.6.0"],
    tests_require=["pytest", "pytest-qt"],
    entry_points={
        'console_scripts': [
            'PartSeg = PartSeg.launcher_main:main',
            'Tester = PartSeg.test_widget_main:main'
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha"
    ],
)
