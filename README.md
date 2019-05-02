# ExCars

[![Travis CI](https://api.travis-ci.org/excars/excars-back.svg?branch=master)](https://travis-ci.org/excars/excars-back)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/f0a879aa99e14f88835e85fc44e66fde)](https://www.codacy.com/app/unmade/excars-back?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=excars/excars-back&amp;utm_campaign=Badge_Grade)
[![codecov](https://codecov.io/gh/excars/excars-back/branch/master/graph/badge.svg)](https://codecov.io/gh/excars/excars-back)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![pyup](https://pyup.io/repos/github/excars/excars-back/shield.svg)](https://pyup.io/account/repos/github/excars/excars-back/)

This is backend for [ExCars](https://github.com/excars) project - carpool application that helps you get to work!

## Quickstart

Create `secrets.env` file with following content:

```
GOOGLE_OAUTH2_CLIENT_ID=<...>
```

and hit:

```bash
docker-compose up
```

## API

Checkout project [wiki](https://github.com/excars/excars-back/wiki) page for API documentation

## Development

To install dependencies:

```bash
pipenv install --dev
```

Add pre-commit hooks:

```bash
pre-commit install
```

Run tests:
```bash
docker-compose run --rm app pytest
```
