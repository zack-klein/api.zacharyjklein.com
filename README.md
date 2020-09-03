# api.zacharyjklein.com

![Tag](https://img.shields.io/github/v/tag/zack-klein/api.zacharyjklein.com.svg) [![Build Status](https://travis-ci.com/zack-klein/api.zacharyjklein.com.svg?branch=master)](https://travis-ci.com/zack-klein/api.zacharyjklein.com) [![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://pypi.python.org/pypi/ansicolortags/)

:warning: **WARNING:** I'm no longer actively maintaining this repo. It's still running because some stuff I wrote a while ago depends on it, but I fully intend to deprecate it officially eventually.

This is the backend API service for [zacharyjklein.com](https://zacharyjklein.com).  This code handles the functionality that requires more heavy lifting than simple web interfaces.  This also includes some scheduled jobs that get invoked by Apache Airflow.

# Development
Like most other things I do, I use `docker-compose` to develop locally:
```bash
docker-compose run --rm api

```
Apply canonical code format:
```bash
sh scripts/format.sh
```
