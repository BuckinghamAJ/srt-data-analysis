FROM apache/superset

USER root

ADD superset_config.py /app/superset/
ADD requirements.txt /app/superset/
ADD bin/* /app/superset/
ADD conf/passwd /etc/passwd

ARG username
ARG password

RUN apt-get update \
    && apt-get upgrade -y 

RUN pip install -r /app/superset/requirements.txt

ENV SUPERSET_CONFIG_PATH=/app/superset/superset_config.py

#RUN superset superset db upgrade

#RUN superset superset fab create-admin --username ${username} --password ${password} --firstname Superset --lastname Admin --email srt@gsa.gov

#RUN superset superset init

# Switching back to using the `superset` user
#USER superset

EXPOSE 8080

RUN chmod +x /app/superset/start_superset.sh

CMD ["/app/superset/start_superset.sh"]

