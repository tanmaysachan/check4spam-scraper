import time
from selenium import webdriver
import pandas as pd
import re
import pickle
import os
import urllib.request


cnt = 1


init = {
    "url": [],
    "raw_text": [],
    "image_links": [],
    "tweets_text": [],
    "tweet_ids": [],
}

urls = {
    "page_idx": 1,
    "urls" : set(),
}

story_num = 0

# preload urls pickle if it exists
try:
    with open('urls.pickle', 'rb') as f:
        urls = pickle.load(f)
    print('urls.pickle found and loaded!')
except:
    print('urls.pickle not found. File will be created.')
    pass


# check if data.pickle exists.
# load if it does
try:
    with open('data.pickle', 'rb') as f:
        init = pickle.load(f)
    print("data.pickle found and loaded!")
except:
    print("data.pickle not found. File will be created.")
    pass

for url in urls["urls"]:
    if url in init["url"]:
        continue

    browser.get(url)
    time.sleep(10)

    try:
        article = browser.find_element_by_class_name('entry-content')
    except:
        continue

    paras = article.find_elements_by_tag_name('p')
    text = ""
    for p in paras:
        text += p.text
        text += '\n'

    text = text.replace('\n', ' ')
    images = article.find_elements_by_tag_name('img')

    links = []
    for img in images:
        link = img.get_attribute('srcset').split(' ')[0]
        links.append(link)

    for i in range(len(links)):
        filename = './fn_imgs/'+str(hash(url))+'_'+str(i)+'.jpg'
        urllib.request.urlretrieve(links[i], filename)

    links = ','.join([i for i in links if i is not None])

    tweet_obj = article.find_elements_by_tag_name('twitter-widget')
    tweets_text = ""
    tweet_ids = []
    for obj in tweet_obj:
        tweets_text += obj.text
        tweets_text += '^'
        tweet_ids.append(obj.get_attribute('data-tweet-id'))

    tweets_text = tweets_text.replace('\n', ' ')
    tweet_ids = [i for i in tweet_ids if i is not None]
    tweet_ids = ','.join(tweet_ids)

    init["raw_text"].append(text)
    init["image_links"].append(links)
    init["tweets_text"].append(tweets_text)
    init["tweet_ids"].append(tweet_ids)
    init["url"].append(url)

    if cnt % 5 == 0:
        with open('data.pickle', 'wb+') as f:
            pickle.dump(init, f)
        print("+5 pages scraped and dumped")

    cnt += 1

if os.path.isfile('data.csv'):
    os.replace('data.csv', 'data_backup.csv')
df = pd.DataFrame(init, columns=["url", "raw_text", "image_links", "tweets_text", "tweet_ids"])
df.to_csv('data.csv', index=True, header=True, sep=">")
