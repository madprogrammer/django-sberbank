.PHONY: dist

dist:
	python3.5m setup.py sdist bdist_wheel

upload: dist
	twine upload dist/*

