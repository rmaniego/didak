rm -fr dist/*
py -m build
py setup.py sdist bdist_wheel
py -m twine upload dist/*