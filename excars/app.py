import sanic
import sanic_cors
import sanic_jwt
from playhouse.db_url import connect

import excars.settings
from excars import db as db_utils
from excars.auth.views import authenticate

app = sanic.Sanic()
app.config.from_object(excars.settings)

sanic_jwt.Initialize(app, authenticate=authenticate)
sanic_cors.CORS(app, automatic_options=True)

db = connect(app.config.DB_DSN, database=None)
app.db = db

app.register_listener(db_utils.setup_db, 'before_server_start')
