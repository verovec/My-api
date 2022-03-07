import os.path
import os
from uuid import uuid4

from flask import jsonify

from pathlib import Path
from app.core.mail import get_mail, put_mail, post_mail, delete_mail, search_mail, send_mail_to


def search():
    try:
        resp = search_mail()
    except Exception as e:
        return jsonify(str(e)), 404
    return jsonify(resp)


def get(ids):
    try:
        resp = get_mail(ids)
    except Exception as e:
        return jsonify(str(e)), 404
    return jsonify(resp), 200


def put(ids, **kwargs):
    try:
        resp = put_mail(ids, **kwargs['mail'])
    except Exception as e:
        return jsonify(str(e)), 403
    return jsonify(resp), 200


def post(**kwargs):
    try:
        resp = post_mail(**kwargs['mail'])
    except Exception as e:
        return jsonify(str(e)), 403
    return jsonify(resp), 200


def delete(ids):
    try:
        resp = delete_mail(ids)
    except Exception as e:
        return jsonify(str(e)), 403
    return jsonify(resp), 200


def send_mail(type, mail_address):
    try:
        resp = send_mail_to(type, mail_address)
    except Exception as e:
        return jsonify(str(e)), 403
    return jsonify(resp), 200 
