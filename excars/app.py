import sanic
import sanic_cors

import excars.settings
from excars import auth, db

app = sanic.Sanic()
app.config.from_object(excars.settings)

sanic_cors.CORS(app, automatic_options=True)

app.register_listener(db.init, 'before_server_start')
app.register_listener(auth.init, 'before_server_start')
