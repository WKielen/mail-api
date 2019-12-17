#!/usr/bin/python
# -*- encoding: utf-8 -*-
import os
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, Response, request, jsonify, make_response, json

from flask_cors import CORS
import pkg_resources
import smtplib
import time
import yaml
import jwt
from pywebpush import webpush

app = Flask(__name__)
cors = CORS()
cors.init_app(app, origins='*')

version = pkg_resources.require('mailapi')[0].version

# read config file which should be in the parent directory
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
    tokens = cfg['tokens']
    jwt_secret = tokens['jwt_secret']

    vapid = cfg['vapid']
    vapid_secret_key = vapid['secret_key']
    vapid_public_key = vapid['public_key']
    vapid_private_key = vapid['private_key']
    vapid_claims = vapid['claims']


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return 'Token is missing', 401

        try:
            token_string = token.split();
            data = jwt.decode(token_string[1], jwt_secret)
            roles = data['role'].split(',')
            if not ('AD' in roles or 'LM' in roles or 'LL' in roles):
                return 'Invalid role. Please acquire a proper role.', 401
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 401
        except jwt.exceptions.InvalidSignatureError:
            return 'Invalid token. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401
        except Exception as exc:
            return 'Token is invalid', 401

        return f(*args, **kwargs)

    return decorated


@app.route('/', methods=['GET'])
def i_am_alive_to_browser():
    return 'WebSpace: the final frontier. These are the voyages of version ' + version + '. The mission: to explore strange new languages, <br>to seek out new life and new civilizations, to boldly go where no man has gone before.', 200


# @app.route('/', methods=['OPTIONS'])
# def cors_handler():
#     print(resp)
#     resp = make_response()
#     resp.headers['Access-Control-Allow-Methods'] = 'POST, GET, PATCH, DELETE, OPTIONS'
#     resp.headers['Access-Control-Allow-Headers'] = '*'
#     return resp, 200


@app.route('/mail', methods=['POST'])
@token_required
def send_mail():
    data = request.get_json()
    email_user = data['UserId']
    email_password = data['Password']

    try:
        with smtplib.SMTP('server72.hosting2go.nl', 2525) as smtp:
            smtp.starttls()
            smtp.login(email_user, email_password)

            for mailItem in data['MailItems']:

                msg = MIMEMultipart()
                msg['From'] = mailItem['From']
                msg['To'] = mailItem['To']
                msg['CC'] = mailItem['CC']
                msg['BCC'] = mailItem['BCC']
                msg['Subject'] = mailItem['Subject']

                body = ''
                for line in mailItem['Message']:
                    body += line + '\n'

                to_addresses = [mailItem['To']] + [mailItem['CC']] + [mailItem['BCC']]

                msg.attach(MIMEText(body, 'plain'))
                smtp.sendmail(mailItem['From'], to_addresses, msg.as_string())
                time.sleep(1)
            smtp.quit()

    except smtplib.SMTPRecipientsRefused:
        return 'Mail Error. All recipients were refused. Nobody got the mail.', 200
    except smtplib.SMTPHeloError:
        return 'Mail Error. The server did not reply properly to the HELO greeting.', 200
    except smtplib.SMTPSenderRefused as exc:
        return 'Mail Error. The server did not accept the from_address.', 200
    except smtplib.SMTPDataError as exc:
        return 'Mail Error. The server replied with an unexpected error code (other than a refusal of a recipient).', 200
    except smtplib.SMTPNotSupportedError as exc:
        return 'Mail Error. SMTPUTF8 was given in the mail_options but is not supported by the server.', 200
    except Exception as exc:
        return 'Mail Error. Something went wrong. ', 200
    return 'Success', 200


def send_web_push(subscription_information, message_body):
    return webpush(
        subscription_info=subscription_information,
        data=message_body,
        vapid_private_key=vapid_private_key,
        vapid_claims=vapid_claims
    )


@app.route('/notification', methods=['POST', 'GET'])
@token_required
def send_notification():
    if request.method == "GET":
        return Response(response=json.dumps({"public_key": vapid_public_key}),
                        headers={"Access-Control-Allow-Origin": "*"},
                        content_type="application/json")

    print("is_json", request.is_json)

    if not request.json or not request.json.get('sub_token'):
        return jsonify({'failed': 1})
    if not request.json.get('message'):
        return jsonify({'failed': 1})

    print("request.json", request.json)

    token = request.json.get('sub_token')
    notificationpayload = request.json.get('message')
    try:
        token = json.loads(token)
        send_web_push(token, notificationpayload)
        return jsonify({'success': 1})
    except Exception as e:
        print("error", e)
        return jsonify({'failed': str(e)})


def main():
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
    return


if __name__ == '__main__':
    main()
