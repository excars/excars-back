FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8

ENV APP_HOME="/app"
ENV PYTHONPATH="${APP_HOME}"

RUN pip install pipenv

COPY Pipfile /
COPY Pipfile.lock /

RUN apk add --virtual .build-deps gcc libc-dev \
    && pipenv install --system --ignore-pipfile --deploy --dev \
    && pip install starlette==0.12.0.b3 \
    && apk del .build-deps gcc libc-dev

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}
