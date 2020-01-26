'''
Leverage InstagramAPI
'''
import sys, os, time, json, logging
import networkx
import pandas as pd
import numpy as np
from InstagramAPI import InstagramAPI
from InstaNetwork import customapi


def customapiloader(customapi):
    '''
    WA to apply custom api function
    :param customapi:
    :return:
    '''
    for func in dir(customapi):
        if "__" not in str(func):
            print("[InstaNetwork] Custom loader api for {0}.".format(func))
            setattr(InstagramAPI, str(func), func)
    return InstagramAPI


def start(username=None, password=None):
    '''
    Initialize api with credential work around
    :param username:
    :param password:
    :return: api
    '''
    InstagramAPI = customapiloader(customapi)
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
        api.login_challenge(link)
        api.login()
    except Exception as e:
        if api.LastResponse.ok:
            print("Successfully Login.")
        else:
            print("Failed: {0}".format(str(e)))
    return api


def getfulluserfeed(api, user_id):
    '''
    WARNING!! it will consume alot of requests!
    :param api:
    :param user_id:
    :return:
    '''
    userfeeddf = pd.DataFrame()
    next_max_id = True
    while next_max_id:
        if next_max_id is True:
            next_max_id = ''
        _ = api.getUserFeed(user_id, maxid=next_max_id)
        feeddf = pd.read_json(json.dumps(api.LastJson['items']))
        userfeeddf = pd.concat([userfeeddf, feeddf], ignore_index=True)
        next_max_id = api.LastJson.get('next_max_id', '')
    return userfeeddf


def targetcommentmedia(api, user_id, target_id):
    '''
    TODO : add multithread ops
    api.getUserFeed(user_id)
    userdf = pd.read_json(json.dumps(api.LastJson['items']))
    print(api.LastJson.get('next_max_id', ''))
    :param api:
    :param user_id:
    :param target_id:
    :return:
    '''
    userdf = getfulluserfeed(api, user_id)
    bulkdf = pd.DataFrame()
    if len(userdf) > 0:
        print(len(userdf), len(userdf['pk'].tolist()))
        for media, cap in zip(userdf['pk'].tolist(), userdf['caption'].tolist()):
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

