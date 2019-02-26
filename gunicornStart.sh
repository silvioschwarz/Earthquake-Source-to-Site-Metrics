#! /bin/sh
gunicorn -c gunicorn.conf -b 0.0.0.0:6000 app:server
