from setuptools import Extension, setup

ext_modules = [Extension(name='calc', sources=['extension/calc.c'])]

setup(name='Extensions', ext_modules=ext_modules)
