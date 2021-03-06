import os
import csv
import json
import requests
import threading
from config import Auth_key, main_site, login
import base64
import aiohttp
import asyncio
import threading
import time

credentials = login + ':' + Auth_key

token = base64.b64encode(credentials.encode())
#url_link="https://coxinform.com/wp-json/wp/v2/posts"


def restImg(id,site):
    url=f'{main_site}wp-json/wp/v2/media'
    data = open(f"{site[site.rfind('/')+1:site.find('.')]}/pics/{id}.jpg", 'rb').read()
    fileName = os.path.basename(f"{site[site.rfind('/')+1:site.find('.')]}/{id}.jpg")
    curHeaders = {
        'Authorization': 'Basic ' + token.decode('utf-8'),
        "Content-Type": 'image/jpg',
        'Content-Disposition': 'attachment; filename=%s' % fileName,
    }
    res = 0
    with requests.Session() as s:
        res = s.post(url=f'{main_site}wp-json/wp/v2/media',
                            data=data,
                            headers=curHeaders)
    # pp = pprint.PrettyPrinter(indent=4) ## print it pretty. 
    # pp.pprint(res.json()) #this is nice when you need it
    newDict = res.json()
    newID = newDict.get('id')
    return newID
def restTag(id,site):
    url=f'{main_site}wp-json/wp/v2/tags'
    data = open(f"{site[site.rfind('/')+1:site.find('.')]}/tags/{id}.txt", 'r').read()
    fileName = os.path.basename(f"{site[site.rfind('/')+1:site.find('.')]}/{id}.jpg")
    curHeaders = {
        'Authorization': 'Basic ' + token.decode('utf-8')
    }
    post = {
        'name': data
    }
    res = 0
    with requests.Session() as s:
        res = s.post(url=f'{main_site}wp-json/wp/v2/categories',headers=curHeaders, json=post)
    # pp = pprint.PrettyPrinter(indent=4) ## print it pretty. 
    # pp.pprint(res.json()) #this is nice when you need it
    newDict = res.json()
    newID = newDict['id']
    return newID


def download_tag(site, numb_of_hundred):
    header = {
                    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
                    }
    url = site + f"/wp-json/wp/v2/tag?per_page=100&offset={numb_of_hundred}"
    data = 0
    with requests.Session() as s:
        data = s.get(url=url, headers=header)

    for item in data.json():
        
        out = open(f"{site[site.rfind('/')+1:site.find('.')]}/tags/{item['id']}.txt", "w")
        out.write(item['name'])
        out.close()
        print(f"???????????? ?????? ?? ??????????:{site}; ?? ID: {item['id']}; ??????: {item['name']}")

def download_pic(site, numb_of_hundred):
    header = {
                'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
            }
    url = site + f"/wp-json/wp/v2/media?per_page=100&offset={numb_of_hundred}"
    data = requests.get(url=url, headers=header)

    for item in data.json():
        p = 0
        with requests.Session() as s:
            p = s.get(item['source_url'], headers=header)
        out = open(f"{site[site.rfind('/')+1:site.find('.')]}/pics/{item['id']}.jpg", "wb")
        out.write(p.content)
        out.close()
        print(f"???????????? ???????????????? ?? ??????????:{site}; ?? ID: {item['id']}")

def get_and_post(site, numb_of_hundred):
    
    header = {
                    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
                    }
    url = site + f"/wp-json/wp/v2/posts?per_page=100&offset={numb_of_hundred}"
    data = 0
    with requests.Session() as s:
        data = s.get(url=url, headers=header)
    
    for item in data.json():
        media_id = item['featured_media']
        media_id = restImg(media_id, site)
        
        headers = {'Authorization': 'Basic ' + token.decode('utf-8'), 'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0'}
        post = {
        'title'    : item['title']['rendered'],
        'status'   : 'publish', 
        'content'  : item['content']['rendered'],
        'slug': item['slug'], # category ID
        'date'   : item['date'],
        'featured_media': media_id,
        }
        time.sleep(1)
        with  requests.Session() as s:
            p = s.post(url=f'{main_site}wp-json/wp/v2/posts', headers=headers,json=post)
            print(p.status_code, item['title'])

if __name__ == '__main__':
    with open('sites.txt','r') as f:
        sites = f.read()

    sites = sites.split('\n')
    print(sites)
    for site in sites:
        try:
            os.mkdir(site[site.rfind('/')+1:site.find('.')])
            os.mkdir(site[site.rfind('/')+1:site.find('.')]+'/pics')
            os.mkdir(site[site.rfind('/')+1:site.find('.')]+'/tags')
        except Exception as e:
            pass
        
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
        }
        url = site + "/wp-json/wp/v2/posts"

        count_of_posts = 0
        with requests.Session() as s:
            count_of_posts = s.get(url=url, headers=header).headers['X-WP-Total']
        print(f'??????-???? ???????????? ???? ??????????({site}): {count_of_posts}')
        
        url = site + "/wp-json/wp/v2/media"
        count_of_media = 0
        with requests.Session() as s:
            count_of_media = s.get(url=url, headers=header).headers['x-wp-total']

        url = site + "/wp-json/wp/v2/tags"
        count_of_tags = 0
        with requests.Session() as s:
            count_of_tags = s.get(url=url, headers=header).headers['x-wp-total']


        print(f'??????-???? ?????????? ???? ??????????({site}): {count_of_media}')
        """ print('\n???????????????? ??????????...')
        threads = []
        if int(count_of_media) // 100 > 0:
            for i in range(0,(int(count_of_posts) // 100) + 1):
                thread = threading.Thread(target=download_pic,args=(site,i*100,))
                threads.append(thread)
                print(f'starting bot ???{i}')
                thread.start()
        else:
            download_pic(site,0)
        for thread in threads:
            thread.join() """
        print("?????????? ??????????????!")
        """ print("???????????????? ????????")
        threads = []
        if int(count_of_tags) // 100 > 0:
            for i in range(0,(int(count_of_tags) // 100) + 1):
                thread = threading.Thread(target=download_tag,args=(site,i*100,))
                threads.append(thread)
                print(f'starting bot ???{i}')
                thread.start()
        else:
            download_tag(site,0)
        for thread in threads:
            thread.join()
        print("???????? ??????????????") """

        if int(count_of_posts) // 100 > 0:
            for i in range(0,(int(count_of_media) // 100) + 1):
                thread = threading.Thread(target=get_and_post,args=(site,i*100,))
                print(f'starting bot ???{i}')
                thread.start()
        else:
            get_and_post(site,0)









            
                

        
        

        




""" headers = \
{
    'User-Agent':'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
    'X-WP-Total':''
}
def count_overlapping_substrings(haystack, needle):
    count = 0
    i = -1
    while True:
        i = haystack.find(needle, i+1)
        if i == -1:
            return count
        count += 1
data = requests.get(url=url_link, headers=headers)
str = data.text

url_link="https://coxinform.com/wp-json/wp/v2/posts"
data = requests.get(url=url_link, headers=headers)
print(data.text)

print(data.headers['X-WP-Total']) """