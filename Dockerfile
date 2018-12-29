FROM excars/excars-base:latest

ENV APP_HOME="/excars-back"
ENV PYTHONPATH="${APP_HOME}"

COPY Pipfile /
COPY Pipfile.lock /

RUN pipenv install --system --ignore-pipfile --deploy --dev && pip uninstall ujson -y

WORKDIR ${APP_HOME}
COPY . ${APP_HOME}

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["web"]
