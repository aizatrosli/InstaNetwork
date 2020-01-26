def login_challenge(self, checkpoint_url):
    '''
    This is workaround for challenge login.
    source : https://github.com/LevPasha/Instagram-API-python/issues/718
    :param self:
    :param checkpoint_url:
    :return:
    '''
    import logging
    import json
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


def getUsernameId(self, username):
    '''
    username_id lookup using search method
    :param self:
    :param username: username string
    :return: username_id value
    '''
    if self.SendRequest('users/' + str(username) + '/usernameinfo/'):
        return self.LastJson['user']['pk']
    else:
        return False


def getHighLevelNodeProfile(self, user):
    '''
    get high level detail of user
    :param self:
    :param user: usernameid or username
    :return: pk,username,is_private,follower_count,following_count
    '''
    if str(user).isdigit() and self.SendRequest('users/' + str(user) + '/info/'):
        return self.LastJson
    elif self.SendRequest('users/' + str(user) + '/usernameinfo/'):
        return self.LastJson





