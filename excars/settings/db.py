import os

DB_DSN = os.getenv(
    'DB_DSN',
    'postgresext://excars:excars@db:5432/excars'
)
