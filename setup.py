from distutils.core import setup

setup(
    name='Automate',
    version='0.1.3',
    author='Colin Jermain',
    author_email='clj72@cornell.edu',
    packages=['automate', 'automate.instruments', 'automate.composites'],
    scripts=[],
    url='',
    license='LICENSE.txt',
    description='Automation objects for instrument control',
    long_description=open('README').read(),
    install_requires=[
        "Numpy >= 1.6.1",
        "pandas >= 0.14",
    ],
)
