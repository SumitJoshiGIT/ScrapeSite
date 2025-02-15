import aiohttp as aio
import asyncio
from random import choice,randint
from selectolax.parser import HTMLParser
import re,aiofiles
import time
from json import dumps
from aiocsv import AsyncWriter
import uuid
from fake_useragent import UserAgent

agent=UserAgent()
headers={
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    'Accept-Encoding':'gzip, deflate, br, zstd',
    'Cache-Control':'no-cache',
    'Accept-Charset': 'utf-8',
    'DNT': '1'
}

class LeadScraper():
    def __init__(self,proxy=None):
        self.data=[]
        self.data_=[]
        self.files={}
        self.proxy=proxy
        self.min=10
        self.count=0
        self.requests=0
        self.pg=1
        self.query_tasks=[]
        
        
    async def handler(self):        
            while True:
             if self.query_tasks: 
              query=self.query_tasks.pop()
              self.q= f"site:{query[4]}  @gmail.com {query[2]} {query[3]} Followers @yahoo.com @icloud.com  @outlook.com"     
              ctime=time.time()
              self.pg=query[1]
              self.min=query[0]
              print('[Started]:',ctime)
              await asyncio.gather(*[self.fetch_search_results(query[6]) for i in range(0,3)])
              print(self.count,self.requests,self.min)
              ctime=time.time()-ctime  
              await self.write_results_to_csv(f'./files/{query[5]}_{query[6]}.csv',query[2],query[3],query[4])   
              self.files.pop(query[6])
              #await self.send_json_to_webhook(query[5],query[2],query[3],query[4],ctime,self.pg,query[1],self.min)
              print('done :',ctime)   
             else:await asyncio.sleep(1) 
             self.data=[]
    
    async def send_json_to_webhook(self,url,niche,location,site,t,p,s,n):
     data=dumps({'niche':niche,
                 'location':location,
                 'site':site,
                 'time':t,
                 '_pos':p,
                 '_start':s,
                 '_n':n,
                 'data':self.data[:n]                 
                 })
     
     async with aio.ClientSession() as session:
        async with session.post(url, json=data) as response:
          print(response.status)
    
    async def write_results_to_csv(self,filename,*args):
     async with aiofiles.open(filename, 'a', newline='', encoding='utf-8') as file:
        writer = AsyncWriter(file)
        await writer.writerow(['Niche','Location','Site','Link','Title','Followers', 'Following', 'Email']) 
        for item in self.data[:self.min]:
           await writer.writerow((*args,*item))
        self.count=0

    async def fetch_search_results(self,uid):
        async with aio.ClientSession() as session:
            counter = 0
            tries=30
            while self.files[uid]<self.min and tries:
                h = headers
                count = 0
                h['User-Agent'] = agent.random
                self.pg += 1
                if counter == 25:
                    session.cookie_jar.clear()
                    counter = 0
                url = f'https://www.bing.com/search?first={int(self.pg * 50)}&count=50&q={self.q}&rdr=1'
                async with session.get(url, headers=h, proxy=self.proxy) as response:
                    html = await response.text()
                    soup = HTMLParser(html, 'html.parser').css('.b_algo')
                link = ''
                
                count=self.parse(soup,uid,"l",'m')
                self.files[uid]+= count
                if(count):tries=30
                else:tries-=1 
                print(count)
                count = 0
                counter += 1
    def parse(self,items,uid,*args):
                count=0
                for item in items:
                    data_text = item.css_first('.b_caption').text()
                    email = re.search(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[+A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+', data_text)
                    email=email.group() if email else None
                    link =item.css_first('div.b_attribution cite')
                    link=link.text() if link else '' 
                    pattern = r'https:\/\/www\.instagram\.com\/([a-zA-Z0-9._-]+)(:\/(reel|p|reels|followers|follower|following).*)?\/?'
                    username=re.search(pattern,link)
                    following = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Following', data_text)
                    following = (following.group(1)).replace('K','000').replace('M','000000').replace(',','') if following else ''
                    followers = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?[KM]?) Followers', data_text)
                    followers = (followers.group(1)).replace('K','000').replace('M','000000').replace(',','') if followers else ''
                    username=username.group(1) if username else None
                    if username in ('reel','p','reels','followers','follower','following'):username=None  
                    if email and username and followers:    
                         data=(username,email,following,followers,link,*args)
                         self.data.append(data)
                    
                    
                #self.files[uid][0]+=count   
                return count        
    def add(self,data):
            pos=len(self.query_tasks)
            id=str(uuid.uuid4()) 
            self.files[id]=0
            data.append(id)
            self.query_tasks.append(data)  
            return (pos,id)                

if(__name__=='__main__'):
   ls=LeadScraper()
   "http://mxlraznr-rotate:cjyvyy6a20u0@p.webshare.io:80/"
   print(ls.add([100,1,'fitness','haldwani','instagram.com','test_token']))
   asyncio.run(ls.handler())
    