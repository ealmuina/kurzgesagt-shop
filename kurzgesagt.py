import logging
import base64
import json
import os
import pickle

from email.mime.text import MIMEText

from lxml import html
import requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient import errors
from googleapiclient.discovery import build

STORE_URL = 'https://shop-eu.kurzgesagt.org/collections/kurzgesagt-calendars-books'
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Enable logging
logging.basicConfig(
    filename='log.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def send_mail(config):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    message = MIMEText(STORE_URL)
    message['to'] = config['to_addr']
    message['subject'] = 'Añadido el calendario de 12,021!!!'
    message = {'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode()}

    try:
        message = (service.users().messages().send(userId='me', body=message)
                   .execute())
        logger.info('Message Id: %s' % message['id'])
    except errors.HttpError as error:
        logger.error('An error occurred: %s' % error)


def check_site(config):
    response = requests.get(STORE_URL)
    tree = html.fromstring(response.content)
    products = tree.xpath('//div[@class="mt-15 text-sm font-700 max-w-24 mx-auto"]/text()')
    products = list(map(str, products))

    if any('12,021' in x for x in products):
        send_mail(config)

    logger.info('Check made')


def main():
    with open('config.json') as file:
        check_site(json.load(file))


if __name__ == '__main__':
    main()
