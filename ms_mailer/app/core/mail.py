import os.path
import uuid

from pathlib import Path
from app import db
from app.models.Mail import Mail

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.message import EmailMessage


def search_mail():
    result = [mail.as_dict for mail in Mail.query.all()]
    return result


def get_mail(ids):
    mail = Mail.query.filter_by(ids=ids).first()
    if mail is None:
        raise Exception("Can't find mail with id %s" % ids)
    return mail.as_dict


def put_mail(ids, **kwargs):
    mail = Mail.query.filter_by(ids=ids).first()
    if mail is None:
        raise Exception("Can't find mail with id %s" % ids)
    for name, val in kwargs.items():
        setattr(mail, name, val)
    db.session.commit()
    return mail.as_dict


def post_mail(**kwargs):
    try:
        mail = Mail(ids=uuid.uuid4(), **kwargs)
        db.session.add(mail)
        db.session.commit()
    except Exception as e:
        raise e
    return mail.as_dict


def delete_mail(ids):
    try:
        mail = Mail.query.filter_by(ids=ids).first()
        db.session.delete(mail)
    except Exception:
        raise Exception("Can't find mail with id %s" % ids)
    db.session.commit()
    return {'message': 'mail deleted successfully'}


def send_mail_to(type, mail_address):
    try:
        mail = Mail.query.filter_by(type=type).first()
        mail_from = "msmailer.myyt@gmail.com"
        msg = EmailMessage()
        msg.set_content(mail.content)
        msg["Subject"] = mail.subject
        msg["From"] = mail_from
        msg["To"] = mail_address
        context=ssl.create_default_context()
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls(context=context)
            smtp.login(msg["From"], "totovaalaplage")
            smtp.send_message(msg)
    except Exception as e:
        return {"error": str(e)}
    return {"state":"envoyé"}
