FROM apache/superset:latest as base

USER root

WORKDIR /app/superset

ADD . .
ADD conf/passwd /etc/passwd

ARG username=superset_admin
ARG password
ARG environment=development
ENV SUPERSET_ENVIRONMENT=${environment}



RUN apt-get update \
    && apt-get upgrade -y 


RUN pip install --upgrade pip

RUN pip install -r requirements.txt
RUN pip install -e .

ENV SUPERSET_CONFIG_PATH=/app/superset/superset_config.py

RUN chmod +x ./bin/environment_secrets.sh
RUN ./bin/environment_secrets.sh

#RUN superset superset db upgrade

#RUN superset superset fab create-admin --username ${username} --password ${password} --firstname Superset --lastname Admin --email srt@gsa.gov

#RUN superset superset init

# Switching back to using the `superset` user
#USER superset

EXPOSE 8080

FROM base as initialize-superset
    RUN chmod +x ./bin/start_superset_init.sh
    ENTRYPOINT ["./bin/start_superset_init.sh"]
    CMD ["${username}", "${password}"]

FROM base as superset
    RUN chmod +x ./bin/start_superset.sh
    CMD ["./bin/start_superset.sh"]

