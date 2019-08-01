#!/usr/bin/python
# -*- encoding: utf-8 -*-
from functools import wraps
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, make_response
import configparser
import smtplib
import time
import jwt


app = Flask(__name__)

# read config file which should be in the parent directory
configParser = configparser.RawConfigParser()
configFilePath = r'..\settings.txt'
configParser.read(configFilePath)
JWT_KEY = configParser.get('tokens', 'key')


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
            data = jwt.decode(token_string[1], JWT_KEY)
            roles = data['role'].split(',')
            if not ('AD' in roles or 'LM' in roles or 'LL' in roles):
                return 'Invalid role. Please acquire a proper role.', 401
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.', 401
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.', 401
        except Exception as exc:
            return 'Token is invalid', 401

        return f(*args, **kwargs)
    return decorated


@app.route('/', methods=['GET'])
def i_am_alive_to_browser():
    return 'WebSpace: the final frontier. These are the voyages. My mission: to explore strange new languages, <br>to seek out new life and new civilizations, to boldly go where no man has gone before.', 200


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


def main():
    app.run(debug=True)
    return


if __name__ == '__main__':
    # app.run(host='192.168.178.13', port=5000)
    main()
