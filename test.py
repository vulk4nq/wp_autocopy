import os
import csv
import json
import requests
from pprint import pprint
import asyncio
import aiohttp
#url_link="https://coxinform.com/wp-json/wp/v2/posts"
with open('sites.txt','r') as f:
        sites = f.read()

sites = sites.split('\n')
print(sites)
for site in sites:
    try:
        os.mkdir(site[site.rfind('/')+1:site.find('.')])
    except Exception as e:
        pass


async def parse(sites):
    pass


if __name__ == '__main__':
    asyncio.run(parse())
       
                    
                

        
        

        




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