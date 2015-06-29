# -*- coding: utf-8 -*-
import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = 'YOURTOKEN'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'

lista = []

# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    #'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

	if text.startswith('/'):
            if text == '/start':
                reply('Bot enabled')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabled')
                setEnabled(chat_id, False)
            elif text == '/dice' or text == '/dice@montabot':
                textos = textos = ["En mi cabeza tenia sentido...",
                          "Montagoooooon",
                          "Conozco un atajo",
                          "Perdi",
                          "Cuarta matricula",
                          "FOSTER",
                          "Sera que cabron",
                          "¡Uy! ¡Perdone! (a una papelera)",
                          "Montagon a lo grandeeeee...",
                          "¿Vamos a Cumbres Mayores?",
                          "Mama, ya vaaaa",
                          "Montagon no es un pueblo"]
                n = random.randrange(0, len(textos), 1)
                reply(textos[n])
            elif text == '/notasbd' or text == '/notasbd@montabot':
                textos = ["NOPE",
                          "Cuarta matricula"]
                n = random.randrange(0, len(textos), 1)
                reply(textos[n])
            elif text == '/siono' or text == '/siono@montabot':
                textos = ["Si",
                          "No",
                          "Yo que se",
                          "Cuarta matricula"]
                n = random.randrange(0, len(textos), 1)
                reply(textos[n])
            elif text.startswith('/nuevochiste'):
                texto = text.replace('/nuevochiste', '')
                global lista
                lista.append(texto)
                reply("Nuevo chiste!")
            elif text.startswith('/subirchistes'):
                global lista
                texto = text.replace('/subirchistes', '')
                cadena = ""
                for i in texto:
                    if i != '*':
                        cadena += i
                    else:
                        lista.append(cadena)
                        cadena = ""
                reply("Cargado")
            elif text == '/listadechistes':
                global lista
                reply('\n*\n'.join(lista))
            elif text == '/chiste' or text == '/chiste@montabot':
                global lista
                if len(lista) == 0:
                    reply("NOPE")
                else:
                    n = random.randrange(0, len(lista), 1)
                    reply(lista[n])

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
