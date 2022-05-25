# DESCRIPTION: Dockerfile for praekelt_vaccine_faq_nlp/api_demo_enduser
# BUILD: make image or make image NAME={PROJECT_NAME} PORT={PORT}

FROM praekeltfoundation/python-base:3.9.6
LABEL maintainer="IDinsight"
# Removing this label till we can figure out a good way to update names in Dockerfiles
# LABEL org.opencontainers.image.source="https://github.com/IDinsight/praekelt_mc_demo"

ARG NAME
ARG PORT
ARG HOME_DIR=/usr/src/${NAME}

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

RUN useradd -ms /bin/bash -d ${HOME_DIR} container_user
RUN chown -R container_user: ${HOME_DIR}

# No dependencies on src/, config/, etc.
COPY . ${HOME_DIR}
WORKDIR ${HOME_DIR}
RUN ["chmod", "+x", "gunicorn.sh"]

ENV PYTHONPATH "${PYTHONPATH}:${HOME_DIR}"
ENV PORT ${PORT}

EXPOSE ${PORT}

USER container_user

CMD ["./gunicorn.sh"]
