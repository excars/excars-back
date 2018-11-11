import sanic
import sanic_cors
import sanic_jwt
from playhouse.db_url import connect
from social_flask_peewee.models import init_social

import excars.settings
from excars.auth.views import authenticate
from excars.db import create_tables

app = sanic.Sanic()
app.config.from_object(excars.settings)

sanic_jwt.Initialize(app, authenticate=authenticate)
sanic_cors.CORS(app, automatic_options=True)

db = connect(app.config.DB_URL)
init_social(app, db)
create_tables(db)
