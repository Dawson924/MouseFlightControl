from setuptools import setup, Extension

ext_modules = [
    Extension(
        name="calc",
        sources=["extensions/calc.c"]
    )
]

setup(
    name="Extensions",
    ext_modules=ext_modules
)
