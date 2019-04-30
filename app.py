from flask import (
    Flask,
)
import _thread
from functions import hotel_sys_thread
from Router.User import blueprint as UserRouter
from Router.index import blueprint as indexRouter
from Router.order import blueprint as orderRouter
from Router.admin import blueprint as adminRouter
from Router.comments import blueprint as commentsRouter
from Router.static import blueprint as staticRouter

app = Flask(__name__)
app.register_blueprint(UserRouter, url_prefix="/user")
app.register_blueprint(orderRouter, url_prefix="/order")
app.register_blueprint(adminRouter, url_prefix="/admin")
app.register_blueprint(commentsRouter, url_prefix="/comments")
app.register_blueprint(staticRouter, url_prefix="/static")
app.register_blueprint(indexRouter)
app.secret_key = "zhengyujia"

if __name__ == "__main__":
    config = dict(
        host='0.0.0.0',
        port=3333,
        debug=True,
    )
    thread = _thread.start_new_thread(hotel_sys_thread, ())
    app.run(**config)
