import os

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    'postgresext://excars:excars@db:5432/excars'
)
