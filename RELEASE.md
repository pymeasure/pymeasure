# Release

## PyMeasure package

1. Pull the latest `master` branch
2. `git checkout -b v<version>_release`
3. Update all version references (`grep -rnI '<previous_version>'`)
    - setup.py
    - docs/conf.py
    - pymeasure/__init__.py
4. Update CHANGES.txt with the changelog
5. Push the changes up as a PR
6. Verify that the builds complete
7. Merge the PR
8. Build the source packages
    - `python setup.py bdist_wheel`
    - `pthon setup.py`
9. Create a tagged release on GitHub

## conda-forge feedstock

1. Pull the latest `master` branch
2. `git checkout -b v<version>_release`
3. Download the tarball and determine the sha256 checksum
    - `wget -qO- https://github.com/ralph-group/pymeasure/archive/<version>.tar.gz | sha256sum`
4. Update recipe/meta.yml with the checksum and version number
5. Push the changes up as a PR
6. Verify that the builds complete
7. Merge the PR

## PyPI release

1. Ensure twine is the latest version (`pip install -U twine`)
2. Check the distributions (`twine check dist/*`)
3. Upload the wheel and source distributions to the test server
    - `twine upload --repository-url https://test.pypi.org/legacy/ dist/PyMeasure-<version>-py3-none-any.whl`
    - `twine upload --repository-url https://test.pypi.org/legacy/ dist/PyMeasure-<version>.tar.gz`
4. Verify the test repository: https://test.pypi.org/project/PyMeasure
5. Upload to the real repository (`twine upload dist/PyMeasure-<version>*`)
6. Verify that the package is updated: https://pypi.org/project/PyMeasure
