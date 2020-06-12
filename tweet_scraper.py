#!/usr/bin/env python
# coding: utf-8

# In[13]:


import csv
import time
import tweepy
import json
from tweepy import OAuthHandler
import pandas as pd
import pickle as pkl
import math
from datetime import datetime
import os
import urllib.request


# In[7]:


# Tweepy Initialization

consumer_key = 'LydBaZlcnj64wAhz2zqYSSDG8'
consumer_secret = 'lNDf9f9xcz3qjbXVxcKaF65t8vEvwpDlRQbljwLWS6NOst0rWb'
access_token = '747987764579176448-TmAC6q6EYzK2czKk2wpwSBCycYFjLpd'
access_secret = 'PHaIgoAFNZVdocFVepu3MwrMauzWlDSrTjVBUSrcpUTcD'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth,wait_on_rate_limit=True)


# In[15]:


# Data Loading and file checks
data = pd.read_csv('data.csv',sep='>')
tweets_to_scrape = list(data['tweet_ids'])

if not os.path.exists('tweet_imgs'):
    os.makedirs('tweet_imgs')


# In[21]:


errorIds = []

for tid in tweets_to_scrape:
    if type(tid) != float:
        try:
            tweet_data = api.get_status(int(tid))
            for i in range(len(tweet_data.entities["media"])):
                media =  tweet_data.entities["media"][i]
                filename = './tweet_imgs/'+str(tid)+'_'+str(i)+'.jpg'
                urllib.request.urlretrieve(media['media_url'], filename)
        except:
            errorIds.append(int(tid))
            print(tid)


# In[ ]:


with open('tweetScrapeErrorIds.txt', 'w') as f:
    for item in errorIds:
        f.write("%s\n" % item)

