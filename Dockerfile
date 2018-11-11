FROM python:3.7.1

ENV HOME="/excars"


RUN pip3 install --upgrade pip cython && \
    pip3 install pipenv

COPY Pipfile /
COPY Pipfile.lock /

RUN pipenv install --system --dev

WORKDIR ${HOME}
COPY . ${HOME}

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["web"]
