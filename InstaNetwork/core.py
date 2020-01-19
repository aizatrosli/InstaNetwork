'''
Leverage InstagramAPI
'''
import sys, os, time, json, logging
import networkx
import pandas as pd
import numpy as np
from InstagramAPI import InstagramAPI


def login_challenge(self, checkpoint_url):
    '''
    This is workaround for challenge login.
    :param self:
    :param checkpoint_url:
    :return:
    '''
    BASE_URL = 'https://www.instagram.com/'
    self.s.headers.update({'Referer': BASE_URL})
    req = self.s.get(BASE_URL[:-1] + checkpoint_url)
    self.s.headers.update({'X-CSRFToken': req.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})
    self.s.headers.update({'Referer': BASE_URL[:-1] + checkpoint_url})
    mode = int(input('Choose a challenge mode (0 - SMS, 1 - Email): '))
    challenge_data = {'choice': mode}
    challenge = self.s.post(BASE_URL[:-1] + checkpoint_url, data=challenge_data, allow_redirects=True)
    self.s.headers.update({'X-CSRFToken': challenge.cookies['csrftoken'], 'X-Instagram-AJAX': '1'})

    code = input('Enter code received: ').strip()
    code_data = {'security_code': code}
    code = self.s.post(BASE_URL[:-1] + checkpoint_url, data=code_data, allow_redirects=True)
    self.s.headers.update({'X-CSRFToken': code.cookies['csrftoken']})
    self.cookies = code.cookies
    code_text = json.loads(code.text)
    if code_text.get('status') == 'ok':
        self.authenticated = True
        self.logged_in = True
    elif 'errors' in code.text:
        for count, error in enumerate(code_text['challenge']['errors']):
            count += 1
            logging.error('Session error %(count)s: "%(error)s"' % locals())
    else:
        logging.error(json.dumps(code_text))


def start(username=None, password=None):
    '''
    Initialize api with credential work around
    :param username:
    :param password:
    :return: api
    '''
    InstagramAPI.ver = login_challenge
    api = None
    if username is None and password is None:
        with open(r'..\credential.json') as fp:
            credential = json.load(fp)
            username = credential['username']
            password = credential['password']
    api = InstagramAPI(username, password)
    api.login()
    try:
        link = api.LastJson['challenge']['api_path']
        api.ver(link)
        api.login()
    except Exception as e:
        if api.LastResponse.ok:
            print("Successfully Login.")
        else:
            print("Failed: {0}".format(str(e)))
    return api


def getfulluserfeed(api, user_id):
    userfeeddf = pd.DataFrame()
    next_max_id = True
    while next_max_id:
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFeed(user_id, maxid=next_max_id)
        feeddf = pd.read_json(json.dumps(api.LastJson['items']))
        userfeeddf = pd.concat([userfeeddf,feeddf], ignore_index=True)
        next_max_id = api.LastJson.get('next_max_id', '')
    return userfeeddf


def targetcommentmedia(api, user_id, target_id):
    '''
    api.getUserFeed(user_id)
    userdf = pd.read_json(json.dumps(api.LastJson['items']))
    print(api.LastJson.get('next_max_id', ''))
    '''
    userdf = getfulluserfeed(api, user_id)
    bulkdf = pd.DataFrame()
    if len(userdf) > 0:
        print(len(userdf),len(userdf['pk'].tolist()))
        for media,cap in zip(userdf['pk'].tolist(),userdf['caption'].tolist()):
            max_id = ''
            api.getMediaComments(str(media), max_id=max_id)
            time.sleep(5)
            try:
                commentdf = pd.read_json(json.dumps(api.LastJson['comments']))
                commentdf = commentdf[commentdf['user_id'] == int(target_id)]
                commentdf['caption'] = cap['text']
                commentdf['owner'] = cap['user']['username']
                bulkdf = pd.concat([bulkdf, commentdf], ignore_index=True)
            except:
                logging.error(api.LastJson)
                pass
    return bulkdf, len(userdf)

