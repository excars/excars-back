nopyc:
	@find . -name "*.pyc" -exec rm -f {} \;


isort:
	@isort --check-only -q


flake8:
	@flake8 excars/*


pylint:
	@pylint excars/*


test:
	@pytest


lint: isort flake8 pylint

ci: lint test
