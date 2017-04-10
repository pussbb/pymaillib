# -*- coding: utf-8 -*-
"""

"""
from werkzeug.utils import redirect

from flask_app.controller import Controller, route
from flask_app.helpers.url import build_url


class WelcomeController(Controller):
    resource = ''

    @route('/')
    def index(self):
        return redirect(build_url('MailboxController:root'))
