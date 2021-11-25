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
        print(f"Скачал тэг с сайта:{site}; С ID: {item['id']}; Имя: {item['name']}")

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
        if os.path.exists(f"{site[site.rfind('/')+1:site.find('.')]}/pics/{item['id']}.jpg"):
            continue
        else:
            out = open(f"{site[site.rfind('/')+1:site.find('.')]}/pics/{item['id']}.jpg", "wb")
            out.write(p.content)
            out.close()
            print(f"Скачал картинку с сайта:{site}; С ID: {item['id']}")

def get_and_post(site, numb_of_hundred):
    
    header = {
                    'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
                    }
    url = site + f"/wp-json/wp/v2/posts?per_page=100&offset={numb_of_hundred}"
    data = 0
    with requests.Session() as s:
        data = s.get(url=url, headers=header)
    
    for item in data.json():
        with open(f"{site[site.rfind('/')+1:site.find('.')]}/id.txt",'r') as f:
            strings = f.read()
        string = strings.split('\n')
        flag = False
        
        for id in string:
            if id == str(item['id']):
                flag = True
                print("Уже есть такой")
                continue
        if not flag:        
            media_id = item['featured_media']
            if media_id == 0:
                media_id = 0
            else:
                media_id = restImg(media_id, site)
            with open(f"{site[site.rfind('/')+1:site.find('.')]}/id.txt",'a') as f:
                f.write(f"{item['id']}\n")
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
def main():
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
        with open(f"{site[site.rfind('/')+1:site.find('.')]}/id.txt",'a') as f:
            pass
        header = {
            'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0',
        }
        url = site + "/wp-json/wp/v2/posts"

        count_of_posts = 0
        with requests.Session() as s:
            count_of_posts = s.get(url=url, headers=header).headers['X-WP-Total']
        print(f'Кол-во постов на сайте({site}): {count_of_posts}')
        
        url = site + "/wp-json/wp/v2/media"
        count_of_media = 0
        with requests.Session() as s:
            count_of_media = s.get(url=url, headers=header).headers['x-wp-total']

        url = site + "/wp-json/wp/v2/tags"
        count_of_tags = 0
        with requests.Session() as s:
            count_of_tags = s.get(url=url, headers=header).headers['x-wp-total']


        print(f'Кол-во медиа на сайте({site}): {count_of_media}')
        print('\nСкачиваю медиа...')
        threads = []
        if int(count_of_media) // 100 > 0:
            for i in range(0,(int(count_of_posts) // 100) + 1):
                thread = threading.Thread(target=download_pic,args=(site,i*100,))
                threads.append(thread)
                print(f'starting bot №{i}')
                thread.start()
        else:
            download_pic(site,0)
        for thread in threads:
            thread.join() 
        print("Медиа скачано!")

        if int(count_of_posts) // 100 > 0:
            for i in range(0,(int(count_of_media) // 100) + 1):
                thread = threading.Thread(target=get_and_post,args=(site,i*100,))
                print(f'starting bot №{i}')
                thread.start()
        else:
            get_and_post(site,0)

if __name__ == '__main__':
    x = time.perf_counter()
    main()
    while True:
        if time.perf_counter() - x > 3600:
            main()










            
                

        
        

"""print("Скачиваю тэги")
        threads = []
        if int(count_of_tags) // 100 > 0:
            for i in range(0,(int(count_of_tags) // 100) + 1):
                thread = threading.Thread(target=download_tag,args=(site,i*100,))
                threads.append(thread)
                print(f'starting bot №{i}')
                thread.start()
        else:
            download_tag(site,0)
        for thread in threads:
            thread.join()
        print("Тэги скачаны") """        




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