import os

DB_URL = os.getenv(
    'DB_URL',
    'postgresext://excars:excars@db:5432/excars'
)
