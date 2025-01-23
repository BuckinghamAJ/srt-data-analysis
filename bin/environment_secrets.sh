#!/bin/sh


if [ "$SUPERSET_ENVIRONMENT" = "production" ]; then
    cp /app/superset/conf/client_secrets.prod.json /app/superset/conf/client_secrets.json
elif ["$SUPERSET_ENVIRONMENT" = "staging"]; then
    cp /app/superset/conf/client_secrets.staging.json /app/superset/conf/client_secrets.json
else
    cp /app/superset/conf/client_secrets.dev.json /app/superset/conf/client_secrets.json
fi