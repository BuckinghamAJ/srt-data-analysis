#!/bin/sh

gunicorn -w 3 \
      -k gevent \
      --worker-connections 1000 \
      --timeout 120 \
      -b  0.0.0.0:8080 \
      --limit-request-line 0 \
      --limit-request-field_size 0 \
      "superset.app:create_app()"