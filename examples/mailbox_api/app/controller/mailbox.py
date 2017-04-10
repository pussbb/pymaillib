# -*- coding: utf-8 -*-
"""

"""
import traceback
import weakref
from functools import wraps

from flask import current_app, Response, request
from werkzeug.exceptions import Forbidden, NotFound
from werkzeug.routing import BaseConverter

from flask_app.controller import Controller, route
from pymaillib.imap.entity.body_structure import MessageRFC822BodPart, \
    MultiPartBodyPart
from pymaillib.imap.entity.email_message import EmailMessage, decode_part
from pymaillib.imap.exceptions import ImapClientException
from pymaillib.imap.query.builders.fetch import FetchQueryBuilder
from pymaillib.mailbox import UserMailbox
from pymaillib.settings import Config


class EmailRfc822Response(Response):
    default_mimetype = 'message/rfc822'
    content_type = 'message/rfc822'

    def __init__(self, email: EmailMessage):
        headers = {
            'Content-Type': '{}; charset={};'.format(
                EmailRfc822Response.content_type, email.get_content_charset()),
            'Content-Disposition': 'inline; filename="rfc822.eml";'
        }
        super().__init__(email.as_bytes(), headers=headers)


class FolderIdConverter(BaseConverter):
    regex = '([\w\d]{8,})'

current_app.url_map.converters['fid'] = FolderIdConverter


USER_MAILBOXES = weakref.WeakValueDictionary()


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def get_user_mail_box(auth_data):
    if not auth_data:
        return None
    mailbox = USER_MAILBOXES.get(auth_data.username)
    if not mailbox:
        try:
            imap_conf = Config().from_config_file('./pymail.ini')
            mailbox = UserMailbox(auth_data.username,
                                  auth_data.password, imap_conf)
            mailbox.imap()
        except ImapClientException as _:
            traceback.print_exc()
            raise Forbidden()
        else:
            USER_MAILBOXES[auth_data.username] = mailbox
    else:
        if not mailbox.check(auth_data):
            return None
    return mailbox


def requires_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        mailbox = get_user_mail_box(auth)
        if not auth or not mailbox:
            return authenticate()
        kwargs['mailbox'] = mailbox
        return f(*args, **kwargs)
    return wrapper


class MailboxController(Controller):

    resource = 'api/mailbox'

    decorators = [requires_auth]

    @route('/')
    def root(self, mailbox):
        return {'folders': mailbox.mailboxes()}

    @route('/<fid:folder>/')
    def folder(self, folder, mailbox):
        imap_folder = mailbox.mailboxes().get(folder)
        if not imap_folder:
            raise NotFound
        query = FetchQueryBuilder('1:*') \
            .fetch_rfc822_size() \
            .fetch_envelope() \
            .fetch_flags() \
            .fetch_body_structure()
        with mailbox.imap() as client:
            for msg in client.fetch(imap_folder, query):
                msg['folder'] = imap_folder
                yield msg

    @route('/<fid:folder>/<int:msg_id>/', defaults={'mime_id': None})
    @route('/<fid:folder>/<int:msg_id>/<string:mime_id>/')
    def message(self, folder, mailbox, msg_id, mime_id):
        imap_folder = mailbox.mailboxes().get(folder)
        if not imap_folder:
            raise NotFound

        query = FetchQueryBuilder(uids=msg_id)
        raw = self.request_values.get('raw')
        if mime_id:
            query.fetch_body_structure()
            query.fetch_body(mime_id)
        else:
            query.fetch_rfc822()

        with mailbox.imap() as client:
            email = list(client.fetch(imap_folder, query))[-1]
            if not email:
                raise NotFound('Email with provided uid does not exists'
                               ' anymore')
            if mime_id:
                part_info, data = email.get_fetched_mime_part(mime_id)
                headers = {
                    'Content-Type': '{}; charset={};'.format(
                        part_info.content_part,
                        part_info.charset),

                }
                if not isinstance(part_info, (MessageRFC822BodPart,
                                              MultiPartBodyPart)) and not raw:
                    data = decode_part(part_info, data)
                return Response(data, mimetype=part_info.content_part,
                                headers=headers)
            return EmailRfc822Response(email.rfc822)



