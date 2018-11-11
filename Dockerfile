FROM python:3.7.1

ENV APP_HOME="/excars-back"


RUN pip3 install --upgrade pip cython && \
    pip3 install pipenv

COPY Pipfile /
COPY Pipfile.lock /

RUN pipenv install --system --dev

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["web"]
