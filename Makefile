# Makefile for the Python pyneric project
# This has only been tested with GNU make from within the project root.

SHELL := /bin/bash

all: coverage build doc

flake:
	flake8 src

test: flake
	PYTHONPATH=src:tests coverage run --module unittest discover --start-directory tests/non_django
	PYTHONPATH=src:tests coverage run --append tests/django_test_app/manage.py test django_test_app --noinput
	PYTHONPATH=src python -m doctest docs/examples.rst

coverage: test
	coverage report --fail-under=100

coverage_html: test
	coverage html

build:
	./setup.py build

readme:
	cat README_editable.rst | ( while read; do if [[ $${REPLY#.. include:: } != $${REPLY} ]]; then cat $${REPLY#.. include:: }; else echo $${REPLY}; fi; done ) > README.rst

doc: readme
	$(MAKE) -C docs html

deb:
	./setup.py --command-packages=stdeb.command sdist_dsc --with-python2=True --with-python3=True bdist_deb

deb2:
	./setup.py --command-packages=stdeb.command sdist_dsc --with-python2=True --with-python3=False bdist_deb

deb3:
	./setup.py --command-packages=stdeb.command sdist_dsc --with-python2=False --with-python3=True bdist_deb

clean:
	./setup.py clean -a
	$(MAKE) -C docs clean
	$(RM) MANIFEST
	$(RM) -r dist
	$(RM) -r src/*.egg-info
	$(RM) -r htmlcov
	coverage erase
	find . -type d -name '__pycache__' | xargs $(RM) -r
	find . -type f -name '*.py[co]' | xargs $(RM)
#	git submodule update docs/_build/html
#	git -C docs/_build/html checkout gh-pages

.PHONY: test coverage coverage_html build readme doc clean deb deb2 deb3
