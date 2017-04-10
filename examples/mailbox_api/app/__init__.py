# -*- coding: utf-8 -*-
"""

"""

import flask_app
from flask_app.helpers.app import simple_exception_handler

APP = flask_app.create_app(flask_app.from_module_name(__name__))


with APP.app_context():
    from . import routes


def serve(app_env=None):
    flask_app.serve(APP, app_env)


@APP.errorhandler(Exception)
def handler(*args, **kwargs):
    return simple_exception_handler(*args, **kwargs)
