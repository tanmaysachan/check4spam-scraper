import time
from selenium import webdriver
import pandas as pd
import re
import pickle
import os
import urllib.request
import sys
from tqdm import tqdm

options = webdriver.FirefoxOptions()
options.add_argument('--headless')
options.add_argument('--log-level=3')
browser = webdriver.Firefox('./gecko',options=options)

if not os.path.exists('fn_imgs'):
    os.makedirs('fn_imgs')

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

# populate urls with check4scam scrape
fake_news_url = r"https://check4spam.com/category/internet-rumours/"

pattern = "^https://check4spam.com/[^/]*-[^/]*/$"

blacklist = [
    "https://check4spam.com/contact-us/",
    "https://check4spam.com/fact-search-engine/",
    "https://check4spam.com/coronavirus-fake-news/",
    "https://check4spam.com/about-us/",
    "https://check4spam.com/media-coverage/",
]

pages_to_scrape_for_article_links = 76

for page in tqdm(range(pages_to_scrape_for_article_links)):
    try:
        if page > 75 or urls["page_idx"] > 75:
            # check4spam page 76 doesn't exist.
            break
        new_url = fake_news_url + r"page/" + str(urls["page_idx"])
        browser.get(new_url)
        time.sleep(7)
        links = browser.find_elements_by_tag_name('a')
        for link in links:
            url = link.get_attribute('href')
            if re.match(pattern, url) and url not in blacklist and r'/author/' not in url:
                try:
                    urls["urls"].add(url)
                except:
                    continue

        urls["page_idx"] += 1
    except:
        with open('urls.pickle', 'wb+') as f:
            pickle.dump(urls, f)
        print('Checkpoint. Error in script, data saved.')
        sys.exit(1)

    if page > 75 or urls["page_idx"] > 75:
        # check4spam page 76 doesn't exist.
        break

cnt = 1

init = {
    "url": [],
    "raw_text": [],
    "image_links": [],
    "tweets_text": [],
    "tweet_ids": [],
}

# check if data.pickle exists.
# load if it does
try:
    with open('data.pickle', 'rb') as f:
        init = pickle.load(f)
    print("data.pickle found and loaded!")
except:
    print("data.pickle not found. File will be created.")
    pass

fails = 0

for url in tqdm(urls["urls"]):
    try:
        if url in init["url"]:
            print("url fetched...skipping")
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
            try:
                filename = './fn_imgs/'+str(hash(url))+'_'+str(i)+'.jpg'
                urllib.request.urlretrieve(links[i], filename)
            except:
                print(links[i])

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

        fails = 0

    except:
        with open('data.pickle', 'wb+') as f:
            pickle.dump(init, f)
        print("skipping url, dumping data.")
        fails += 1

        if fails > 5:
            print("Probably a net issue. Exiting script")
            sys.exit(1)

    cnt += 1

if os.path.isfile('data.csv'):
    os.replace('data.csv', 'data_backup.csv')
df = pd.DataFrame(init, columns=["url", "raw_text", "image_links", "tweets_text", "tweet_ids"])
df.to_csv('data.csv', index=True, header=True, sep=">")
