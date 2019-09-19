#!/usr/bin/python
# -*- encoding: utf-8 -*-
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import make_msgid, formatdate
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import pkg_resources
import smtplib
import time
import yaml
import jwt


app = Flask(__name__)
cors = CORS()
cors.init_app(app, origins='*')

version = pkg_resources.require('mailapi')[0].version

# read config file which should be in the parent directory
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.BaseLoader)
    tokens = cfg['tokens']
    jwt_secret = tokens['jwt_secret']


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']

        if not token:
            return jsonify(message='Token is missing'), 401

        try:
            token_string = token.split();
            data = jwt.decode(token_string[1], jwt_secret)
            roles = data['role'].split(',')
            if not ('AD' in roles or 'LM' in roles or 'LL' in roles):
                return jsonify(message='Invalid role. Please acquire a proper role.'), 401
        except jwt.ExpiredSignatureError:
            return jsonify(message='Signature expired. Please log in again.'), 401
        except jwt.exceptions.InvalidSignatureError:
            return jsonify(message='Invalid token. Please log in again.'), 401
        except jwt.InvalidTokenError:
            return jsonify(message='Invalid token. Please log in again.'), 401
        except Exception as exc:
            return jsonify(message='Token is invalid'), 401

        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
def i_am_alive_to_browser():
    return 'WebSpace: the final frontier. These are the voyages of version ' + version + '. The mission: to explore strange new languages, <br>to seek out new life and new civilizations, to boldly go where no man has gone before.', 200


@app.route('/mail', methods=['POST'])
@token_required
def send_mail():
    data = request.get_json()
    email_user = data['UserId']
    email_password = data['Password']

    try:
        with smtplib.SMTP('server72.hosting2go.nl', 587) as smtp:
            smtp.starttls()
            smtp.login(email_user, email_password)

            for mailItem in data['MailItems']:

                msg = MIMEMultipart()
                msg['From'] = mailItem['From']
                msg['To'] = mailItem['To']
                if 'CC' in mailItem:
                    msg['CC'] = mailItem['CC']
                if 'BCC' in mailItem:
                    msg['BCC'] = mailItem['BCC']
                msg['Subject'] = mailItem['Subject']

                body = ''
                for line in mailItem['Message']:
                    body += line + '\n'

                to_addresses = [mailItem['To']]
                if 'CC' in mailItem:
                    to_addresses.append(mailItem['CC'])
                if 'BCC' in mailItem:
                    to_addresses.append(mailItem['BCC'])

                msg.add_header('message-id', make_msgid('squirrel', '72.sslprotected.nl'))
                msg.add_header('reply-to', mailItem['From'])
                msg.add_header('return-path', 'Returned Mail<info@ttvn.nl>')
                msg.add_header('organization', 'Tafeltennisvereniging Nieuwegein')
                msg.add_header('mime-version', '1.0')
                msg.add_header('content-type', 'text/plain;charset=utf-8')
                msg.add_header('importance', 'Normal')
                msg.add_header('user-agent',  'TTVN verenigingsmail')
                msg.add_header('content-transfer-encoding',  '8bit')
                msg.add_header('X-Priority', '3 (Normal)')
                msg.add_header('X-Mailer', 'TTVN verenigingsmail')
                msg.add_header('date', formatdate())

                msg.attach(MIMEText(body, 'plain'))
                smtp.sendmail(mailItem['From'], to_addresses, msg.as_string())
                time.sleep(1)
            smtp.quit()

    except smtplib.SMTPRecipientsRefused:
        return jsonify(message='Mail Error. All recipients were refused. Nobody got the mail.'), 200
    except smtplib.SMTPHeloError:
        return jsonify(message='Mail Error. The server did not reply properly to the HELO greeting.'), 200
    except smtplib.SMTPSenderRefused as exc:
        return jsonify(message='Mail Error. The server did not accept the from_address.'), 200
    except smtplib.SMTPDataError as exc:
        return jsonify(message='Mail Error. The server replied with an unexpected error code (other than a refusal of a recipient).'), 200
    except smtplib.SMTPNotSupportedError as exc:
        return jsonify(message='Mail Error. SMTPUTF8 was given in the mail_options but is not supported by the server.'), 200
    except Exception as exc:
        return jsonify(message='Mail Error. Something went wrong. ' + exc), 200
    return jsonify(message='Success'), 200


def main():
    app.run(host='0.0.0.0', port=5000)
    # app.run(debug=True)
    return


if __name__ == '__main__':
    main()
