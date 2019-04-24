from flask import (
    Blueprint,
    request,
    session,
    redirect,
    url_for,
    render_template,
    make_response,
)


blueprint = Blueprint("static", __name__)

def file_get(f):
    while True:
        yield f.read(1024)


@blueprint.route("/<filename>")
def get_jpg_file(filename):
    data = b''
    path = 'static/'
    filename = path + filename
    with open(filename, "rb") as f:
        data = f.read()
    resp = make_response(data)
    resp.headers["content-type"] = "image/jpeg"
    return resp


