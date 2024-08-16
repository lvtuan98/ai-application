FROM python:3.10.10-buster

ARG http_proxy
ARG https_proxy
ENV http_proxy=${http_proxy}
ENV https_proxy=${https_proxy}

ARG UID=1000
ARG GID=1000
ARG USERNAME=idpuser
# RUN groupadd --gid ${GID} ${USERNAME} \
#     && useradd --uid ${UID} --gid ${GID} -m ${USERNAME} \
#     && apt-get update \
#     && apt-get install -y sudo poppler-utils \
#     && echo ${USERNAME} ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/${USERNAME} \
#     && chmod 0440 /etc/sudoers.d/${USERNAME}
RUN apt-get update && apt-get install -y sudo poppler-utils
RUN apt install -y postgresql gcc musl-dev bash gettext
RUN pip install --upgrade pip && pip install uvicorn gunicorn Celery --no-cache-dir

# USER ${UID}
# ADD --chown=${UID}:${GID} idp-api/idp /app
# COPY --chown=${UID}:${GID} idp-api/requirements/requirements.txt /app

# COPY idp /app
# WORKDIR /app
COPY ./requirements.txt /tmp
RUN pip --default-timeout=1000 install -r /tmp/requirements.txt --no-cache-dir 

# CMD "service cron start"
# COPY --chown=${UID}:${GID} sidp-api/ /app