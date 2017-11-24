#!/usr/bin/env sh

gunicorn -c gunicorn.py.ini app
