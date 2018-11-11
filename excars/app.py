import sanic
from playhouse.db_url import connect

import excars.settings
from excars.db import create_tables

app = sanic.Sanic()
app.config.from_object(excars.settings)


db = connect(app.config.DB_URL)
create_tables(db)
