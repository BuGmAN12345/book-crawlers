from source.Proxies_Pool import Proxies_Pool
from source.Header import User_Agent

from bs4 import BeautifulSoup
from rich.progress import Progress
from ebooklib import epub
import requests
import time
import os
import sys
import random

from source.config import OPTION

host_agent=OPTION["host_agent"] #默认不使用主机代理
basic_path=OPTION["basic_path"]  #存放书籍路径 

class Get_Book:
	def __init__(self,book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool=None): #是否使用代理，代理池大小
		#print("book crawlers is opened……")
		self.book_name=book_name # input("Please enter the name of the book you want to crawl\n") 
		self.whether_Proxies=whether_Proxies
		self.proxies_pool_num=num
		if proxy_pool==None: #并未传入指定代理池
			self.init_proxies()
		else:
			self.proxies_pool=proxy_pool
		#self.headers=Header()
		self.user_agent=User_Agent()
		self.sleep_time=0 #网页出错次数
		self.title=[]
		self.urls=[]
		self._workfile_path=basic_path+r"\workfile"
		self.workfile_path=self._workfile_path+r"\\"
		self.thread_num=thread_num
		self.whether_epub=whether_epub
		self.author=''

	def init_proxies(self):
		if self.whether_Proxies==True:
			pp=Proxies_Pool()
			self.proxies_pool=pp.get_Proxies(self.proxies_pool_num) #获取代理池

	def proxies_request(self,target,method,data):  #运用代理下的请求处理，默认使用get方法
		random_proxies=random.randint(0,len(self.proxies_pool)-1)
		request_time=0
		success=False
		tmp=not host_agent #即默认使用SSL检验
		while success==False: #当代理不对时一直循环       
			while True: #当请求不成功时一直循环
				try:
					ua=self.user_agent.rgua()
					self.headers.perm_replace_header('User-Agent',ua)
					if method==False:
						with requests.get(url=target,headers=self.headers.get_header(),proxies={"http":self.proxies_pool[random_proxies]},timeout=5,verify=tmp) as req:
							if req.history: #如果出现重定位，则自动修正url
								self.server=req.url.rsplit('/', 1)[0]+'/'
								print('server has changed into ',self.server)
							success=True
							if req.status_code==200:
								return req
							elif request_time>5:
								print("in ",target)
								print("-"*20,"network erro!","-"*20)
								sys.exit()
							else:
								#print("sleep! in",target)
								time.sleep(2^request_time) #动态调整休息时间
					else:
						with requests.post(url=target,headers=self.headers.get_header(),data=data,proxies={"http":self.proxies_pool[random_proxies]},timeout=5,verify=tmp) as req:
							if req.history: #如果出现重定位，则自动修正url
								self.server=req.url.rsplit('/', 1)[0]+'/'
								print('server has changed into ',self.server)
							success=True
							if req.status_code==200:
								return req
							elif request_time>5:
								print("in ",target)
								print("-"*20,"network erro!","-"*20)
								sys.exit()
							else:
								time.sleep(2^request_time)
					request_time+=1
					self.sleep_time+=1
				except requests.exceptions.Timeout:  #如果代理不可用
					del self.proxies_pool[random_proxies]
					if not self.proxies_pool:
						print("Proxy resource exhausted. Re-pulling……")
						self.init_proxies(self.proxies_pool_num)
					random_proxies=random.randint(0,len(self.proxies_pool)-1)

	def request(self,target,method,data):
		request_time=0
		tmp=not host_agent #即默认使用SSL检验
		'''proxies = {
	    'http': 'http://127.0.0.1:8080',
	    'https': 'http://127.0.0.1:8080'
	    }'''
		while True:
			ua=self.user_agent.rgua()
			self.headers.perm_replace_header('User-Agent',ua)
			if method==False:
				with requests.get(url=target,headers=self.headers.get_header(),verify=tmp,timeout=5) as req: #proxies=proxies,
					if req.history: #如果出现重定位，则自动修正url
						self.server=req.url.rsplit('/', 1)[0]+'/'
						print('server has changed into ',self.server)
					if req.status_code==200:
						return req
					elif request_time>5:
						print("in ",target)
						print("-"*20,"network erro!","-"*20)
						sys.exit()
					else:
						time.sleep(2^request_time)
			else:
				with requests.post(url=target,data=data,headers=self.headers.get_header(),verify=tmp,timeout=5) as req: #,proxies=proxies
					if req.history: #如果出现重定位，则自动修正url
						self.server=req.url.rsplit('/', 1)[0]+'/'
						print('server has changed into ',self.server)
					if req.status_code==200:
						return req
					elif request_time>5:
						print("in ",target)
						print("-"*20,"network erro!","-"*20)
						sys.exit()
					else:
						time.sleep(2^request_time)
			request_time+=1
			self.sleep_time+=1

	def class_request(self,url,method=False,data=None):
		if self.whether_Proxies==True:
			return self.proxies_request(url,method,data)
		else:
			return self.request(url,method,data)

	def writer(self,title,filename,target):
		text=self.get_contents(target)
		with open(self.workfile_path+filename, 'a', encoding='utf-8') as f:
			if self.whether_epub==True:
				f.write("<h3>{}</h3><br>".format(title))
				f.writelines(text)
				f.write('<br>'*4)
			else: 
				f.write(title+'\n')
				f.writelines(text)
				f.write('\n'*4)

	def copy_and_delete_tofile(self,source_file, destination_file):  #获取文件内容并拷贝到目标文件中，同时删除源文件
		with open(self.workfile_path+source_file, 'r',encoding='utf-8') as source:
			content=source.read()       
		with open(basic_path+r"\\"+destination_file, 'a',encoding='utf-8') as destination:
			destination.write(content)
		os.remove(self.workfile_path+source_file)

	def copy_and_delete(self,source_file):  #获取文件内容并删除源文件
		with open(self.workfile_path+source_file, 'r',encoding='utf-8') as source:
			content=source.read()       
		os.remove(self.workfile_path+source_file)
		return content

	def download_image(self,url,path):
		try:
			response = requests.get(url, stream=True)
			response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常
			with open(path, 'wb') as file:
				for chunk in response.iter_content(chunk_size=8192):
					file.write(chunk)
		except requests.exceptions.RequestException as e:
			print("erro!","-"*50)
			print(e)
			sys.exit()

	def get_cover_picture(self,target,whether_35):
		req=self.class_request(target) #获取图片
		html=req.text
		bf=BeautifulSoup(html,'lxml') 
		if whether_35==True:
			div=bf.find_all('div',id=self.picture_tag)
		else:
			div=bf.find_all('div',class_=self.picture_tag)
		bf=BeautifulSoup(str(div[0]),'lxml')
		pic=bf.find_all('img')
		picture_url=pic[0].get('src')
		self.download_image(self.server+picture_url,self.workfile_path+'cover.jpg')

	def integrate(self,nums,target,whether_35):
		print("Start integrating……")
		if self.whether_epub==False:
			book_txt_name=self.book_name+".txt"
			for i in range(nums):
				txt_name=self.book_name+"_"+str(i)+".txt"
				self.copy_and_delete_tofile(txt_name,book_txt_name)
		else: 
			self.get_cover_picture(target,whether_35) #获取封面
			book=epub.EpubBook()
			book.set_identifier('book')
			book.set_title(self.book_name)
			book.set_language('zh-CN')
			book.add_author(self.author)
			img_path=self.workfile_path+'cover.jpg'
			#image=epub.EpubItem(file_name='cover.jpg',media_type='image/jpeg',content=open(img_path,'rb').read()) #创建封面
			#book.add_item(image)
			book.set_cover(file_name='book_cover.jpg',content=open(img_path,'rb').read(),create_page=True)
			ar_cover=epub.EpubHtml(title=self.book_name,file_name="arcover.xhtml",lang='zh-CN') #创建文字封面
			ar_cover.content="""
			<html>
			<head>
			<style>
				body {{
					margin: 0;
					font-family: Arial, sans-serif;
				}}

				.centered-title {{
					display: flex;
					justify-content: center;
					align-items: center;
					height: 100vh; /* 让 div 铺满整个视口高度 */
				}}

				.centered-title h1 {{
					text-align: center; /* 文字水平居中 */
					color: #333;
					font-size: 3em; /* 调整标题字体大小 */
					margin: 0; /* 去除默认的外边距 */
				}}
			</style>
			</head>
			<body>
				<div class="centered-title">
					<h1>{0}</h1>
					<h2>{1}</h2>
				</div>
			</body>
			</html>""".format(self.book_name,self.author)
			book.add_item(ar_cover)
			c=[]
			with Progress() as progress:
				task=progress.add_task("[cyan]Processing...", total=100)
				for i in range(nums):
					txt_name=self.book_name+"_"+str(i)
					c.append(epub.EpubHtml(title=self.title[i],file_name=txt_name+".xhtml",lang='zh-CN'))
					c[i].content=self.copy_and_delete(txt_name+".txt")
					book.add_item(c[i])
					progress.update(task,advance=(100/nums))
				progress.update(task,completed=100)
			book.toc=((epub.Section('目录'),tuple([c[i] for i in range(nums)])),)
			book.add_item(epub.EpubNcx())
			book.add_item(epub.EpubNav())
			book.spine=[ar_cover]+['nav']+[c[i] for i in range(nums)]
			epub.write_epub(basic_path+r'\{}.epub'.format(self.book_name),book,{})
			os.remove(img_path)

	def call_back(self,task):  #线程池任务异常抛出函数
		try:
			task.result()
		except Exception as e:
			print("something erro occured in the threadpool:\n",e)
			sys.exit()

