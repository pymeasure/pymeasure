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
8. Build and check the source packages
    - `python -m pip install --upgrade build twine`
    - `python -m build`
    - Check the distributions (`twine check dist/*`)
9. Create a tagged release on GitHub

## PyPI release

Official guide [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/).

1. Upload the wheel and source distributions to the test server
    - `python -m twine upload --repository testpypi dist/*`
2. Verify the test repository: https://test.pypi.org/project/PyMeasure
3. Confirm that the installation works (best in a separate environment)
    - `python -m pip install --index-url https://test.pypi.org/simple/ --no-deps pymeasure`
4. Upload to the real repository (`twine upload dist/PyMeasure-<version>*`)
5. Verify that the package is updated: https://pypi.org/project/PyMeasure

## conda-forge feedstock

1. Release to PyPI first (the feedstock pulls from there)
2. Pull the latest `master` branch
3. `git checkout -b v<version>_release`
4. Get the SHA256 hash of the PyPI package at https://pypi.org/project/PyMeasure/#files
5. Update recipe/meta.yml with the checksum and version number
6. Push the changes up as a PR
7. Verify that the builds complete
8. Merge the PR
