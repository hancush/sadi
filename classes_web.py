#!/usr/bin/python

import re
import os
import json
from decimal import *
from collections import defaultdict
from datetime import datetime
from HTMLParser import HTMLParser

from delorean import Delorean, epoch

from slacker import Slacker

class Parser(object):

    def __init__(self, story):
        slack = Slacker(os.environ['ap_key'])
        response = slack.search.messages(query='from:SAM {0}'.format(story),
                                         sort='timestamp',
                                         count=100)
        js = json.loads(response.raw)
        self.results = js['messages']['matches']

    def get_full_image(self, item):
        '''
        Get full image from thumbnail URL.
        '''
        try:
            thumbnail = item['thumb_url']
            parts = [':small', 's150x150']
            for part in parts:
                if part in thumbnail:
                    if part == 'small': # twitter image
                        full_image = re.sub(':small', '', thumbnail)
                    else: # instagram
                        full_image = re.sub('s150x150', 's640x640', thumbnail)
                else: # other image
                    full_image = thumbnail
        except KeyError: # no image
            full_image = ''
        return full_image

    def clean(self, x):
        '''
        Remove brackets, unescape XML.
        '''
        #if '<' or '>' in x:
        #    x = re.sub('<|>', ' ', x)
        parser = HTMLParser()
        x = parser.unescape(x) # unescape &amp;
        x = parser.unescape(x) # unescape xml
        return x   

    def get_post(self, item):
        '''
        Get text of post.
        '''
        try:
            text = item['text'].encode(encoding='utf-8',errors='ignore')
        except:
            text = False
        author = item['author_name'].encode(encoding='utf-8',errors='ignore')
        if text:
            post = '{0}: {1}'.format(author, text)
        else:
            post = author
        post = self.clean(post)
        return post

    def get_actor(self, item):
        '''
        Get name of person who did the thing.
        '''
        full_name = item.split()[:3]
        first_name = full_name[0].lstrip('*')
        if str(full_name[1])[-1] != '*': # the karly exception ^_^
            last_name = '{0} {1}'.format(full_name[1], full_name[2]).rstrip('*')
        else:
            last_name = full_name[1].rstrip('*')
        return first_name, last_name

    def get_action(self, item):
        '''
        Get tags or notes, if applicable.
        '''
        first_name, last_name = self.get_actor(self.text)
        try:
            t = item['fields'][0]
            # Fields in t: 
            # 0 - title (added/deleted)
            # 1 - value (tag/s - separated by \n, if multiple)
            # 2 - short (True/False)
            value = re.sub('\n', ', ', t['value'])
            action = t['title'].lower()
            if len(value.split(',')) == 1: # handle grammar for multiples
                action = '{0} tag {1} by {2} {3}'.format(value, action,
                                                          first_name, last_name)
            else:
                action = '{0} tags {1} by {2} {3}'.format(value, action,
                                                          first_name, last_name)
        except KeyError: # means no tag
            note = item['fallback']
            action = '<i><b>\'{0}\'</b></i> wrote {1} {2}'.format(note, first_name, last_name)
        action = self.clean(action)
        return action

    def get_other(self):
        '''
        Get labels for the following:
        * Story created            * Asset deleted
        * Asset added              * Story deleted
        '''                                            
        message = self.text
        first_name, last_name = self.get_actor(message)
        words = ['added', 'deleted', 'created', 'renamed']
        for word in words:
            if word in message:
                action = '{0} by {1} {2}'.format(word, first_name, last_name)
                break
            else:
                action = self.text
        return action 

    def get_timestamp(self, item):
        '''
        Get timestamp, convert to x days, y hours, z 
        minutes ago format to avoid fancy footwork on
        timezones. (Screw timezones.)
        '''
        unix_timestamp = epoch(float(item['ts']))
        datetime_now = Delorean().epoch
        unix_now = epoch(datetime_now)
        time_since = unix_now - unix_timestamp
        days = time_since.days
        seconds = time_since.seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_since = '{0} days, {1} hours, {2} minutes ago'.format(days, 
                                                                   hours, 
                                                                   minutes) 
        return time_since

    def receive(self):
        '''
        Parse Slack search results, return defaultdict
        with ('image URL', 'post') as key and ['list', 
        'of', 'related', 'actions'] as value.
        '''
        images = []
        posts = []
        actions = []
        timestamps = []

        for item in sorted(self.results, reverse=False):
            timestamp = self.get_timestamp(item)
            timestamps.append(timestamp)
            self.text = item['text']
            try:
                attachments = item['attachments']
                post_info = attachments[0]
                # contains text, author_name, thumb_url
                full_image = self.get_full_image(post_info) 
                images.append(full_image)
                post = self.get_post(post_info) 
                posts.append(post) 
                try:
                    metadata = attachments[1]
                    # contains note/tag info
                    action = self.get_action(metadata) 
                    actions.append(action) 
                except IndexError: # if there ain't no second item
                    action = self.get_other() 
                    actions.append(action)
            except KeyError: # if there ain't no items at all
                post = item['text'] 
                blank_image = '' 
                action = self.get_other() 
                actions.append(action)
                posts.append(post)
                images.append(blank_image)

        first_pass = zip(images, posts)
        second_pass = zip(actions, timestamps)
        third_pass = zip(first_pass, second_pass)

        parsed_data = defaultdict(list)
        for post, action in third_pass:
            parsed_data[post].append(action)

        return parsed_data