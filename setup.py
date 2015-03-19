from distutils.core import setup

setup(
    name='PyMeasure',
    version='0.1.6',
    author='Colin Jermain',
    author_email='clj72@cornell.edu',
    packages=['pymeasure', 'pymeasure.instruments', 'pymeasure.composites'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Measurement automation library for Python instrument control',
    long_description=open('README').read(),
    install_requires=[
        "Numpy >= 1.6.1",
        "pandas >= 0.14",
    ],
)
