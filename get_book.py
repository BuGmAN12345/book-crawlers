from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from prettytable import PrettyTable
from rich.progress import Progress
#import numpy as np
#import pytesseract
#from PIL import Image
import base64
import importlib
#import cv2 as cv
from urllib.parse import quote
from ebooklib import epub
import requests
import hashlib
import string
import time
import re
import os
import sys
import random
import argparse
import wget

host_agent=False #默认不使用主机代理
basic_path=r"C:\Users\34119\Desktop\script library\get_book_ul\books"  #存放书籍路径 

class Proxies_Pool:
	def __init__(self):
		self.proxies_pool=[]  #初始化代理池

	def get_Proxies(self,num):  #从github上获取num个代理
		url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"
		try:
			response = requests.get(url,timeout=5,verify=not host_agent)
			response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常			
		except requests.exceptions.RequestException as e:
			print("erro,failed to get github,please try again or open your vpn and turn the var 'host_agent' into True!","-"*50)
			print(e)
			sys.exit()
		ip_list=response.text.split('\n')
		ip_list=["http://"+ip.strip() for ip in ip_list]
		#print(ip_list)
		self.proxies_pool=ip_list[:num]
		print('Proxy pool initialization completed')
		return self.proxies_pool

class Get_Book:
	def __init__(self,book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool=None): #是否使用代理，代理池大小
		#print("book crawlers is opened……")
		self.book_name=book_name # input("Please enter the name of the book you want to crawl\n") 
		self.whether_Proxies=whether_Proxies
		if proxy_pool==None: #并未传入指定代理池
			self.init_proxies(num)
		else:
			self.proxies_pool=proxy_pool
		self.sleep_time=0 #网页出错次数
		self.title=[]
		self.urls=[]
		self._workfile_path=basic_path+r"\workfile"
		self.workfile_path=self._workfile_path+r"\\"
		self.thread_num=thread_num
		self.whether_epub=whether_epub
		self.author=''

	def init_proxies(self,num):
		if self.whether_Proxies==True:
			pp=Proxies_Pool()
			self.proxies_pool=pp.get_Proxies(num) #获取代理池

	def proxies_request(self,target,method,data):  #运用代理下的请求处理，默认使用get方法
		random_proxies=random.randint(0,len(self.proxies_pool)-1)
		request_time=0
		success=False
		tmp=not host_agent #即默认使用SSL检验
		while success==False:        
			while True:
				try:
					if method==False:
						with requests.get(url=target,headers=self.headers,proxies={"http":self.proxies_pool[random_proxies]},timeout=5,verify=tmp) as req:
							if req.history: #如果出现重定位，则自动修正url
								self.server=req.url.rsplit('/', 1)[0]+'/'
								print('server has changed into ',self.server)
							success=True
							if req.status_code==200:
								return req
							elif request_time>=5:
								print("in ",target)
								print("-"*20,"network erro!","-"*20)
								sys.exit()
							else:
								print("sleep! in",target)
								time.sleep(2)
					else:
						with requests.post(url=target,headers=self.headers,data=data,proxies={"http":self.proxies_pool[random_proxies]},timeout=5,verify=tmp) as req:
							if req.history: #如果出现重定位，则自动修正url
								self.server=req.url.rsplit('/', 1)[0]+'/'
								print('server has changed into ',self.server)
							success=True
							if req.status_code==200:
								return req
							elif request_time>=5:
								print("in ",target)
								print("-"*20,"network erro!","-"*20)
								sys.exit()
							else:
								time.sleep(2)
					request_time+=1
					self.sleep_time+=1
				except requests.exceptions.Timeout:  #如果代理不可用
					del self.proxies_pool[random_proxies]
					random_proxies=random.randint(0,len(self.proxies_pool)-1)

	def request(self,target,method,data):
		request_time=0
		tmp=not host_agent #即默认使用SSL检验
		while True:
			if method==False:
				with requests.get(url=target,headers=self.headers,verify=tmp,timeout=5) as req:
					if req.history: #如果出现重定位，则自动修正url
						self.server=req.url.rsplit('/', 1)[0]+'/'
						print('server has changed into ',self.server)
					if req.status_code==200:
						return req
					elif request_time>=5:
						print("in ",target)
						print("-"*20,"network erro!","-"*20)
						sys.exit()
					else:
						time.sleep(2)
			else:
				with requests.post(url=target,data=data,headers=self.headers,verify=tmp,timeout=5) as req:
					if req.history: #如果出现重定位，则自动修正url
						self.server=req.url.rsplit('/', 1)[0]+'/'
						print('server has changed into ',self.server)
					if req.status_code==200:
						return req
					elif request_time>=5:
						print("in ",target)
						print("-"*20,"network erro!","-"*20)
						sys.exit()
					else:
						time.sleep(2)
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

class Get_Book_35(Get_Book):
	def __init__(self,book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool=None): #是否使用代理，代理池大小
		#print("book crawlers is opened……")
		super().__init__(book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool)
		self.server="https://www.35wx.la"
		self.headers={
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
		"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
		"Accept-Encoding": "gzip, deflate",
		"Referer": "https://www.35wx.la/",
		"Upgrade-Insecure-Requests": "1",
		"Sec-Fetch-Dest": "document",
		"Sec-Fetch-Mode": "navigate",
		"Sec-Fetch-Site": "same-origin",
		"Te": "trailers",
		"Connection": "close"
		}  #目标的请求头，用来说明服务器使用的附加信息
		self.content_tag="ccc"
		self.change_class="bottem2"
		self.picture_tag='fmimg'	

	def search_book(self): #返回需要下载数据的目录地址
		encoded_url=quote(self.book_name)
		url="https://www.35wx.la/modules/article/search.php/?searchkey={}&searchtype=articlename".format(encoded_url)
		req=super().class_request(url)
		html=req.text
		books_name=[]
		books_url=[]
		tr_nr=BeautifulSoup(html,'lxml')
		tr=tr_nr.find_all('tr',id='nr')
		for i in tr:
			td_odd=BeautifulSoup(str(i),'lxml')
			td=td_odd.find_all('td')
			books_name.append([td[0].string,td[2].string]) #获取书名，作者（注：想要获取字数则添加td[3].string,最后更新时间添加td[4].string）
			a=td_odd.find_all('a')
			books_url.append(a[0].get('href'))
		if len(books_name)!=len(books_url):
			print("something erro!")
			sys.exit()
		if len(books_name)==0:
			print("please try again,the keyword is not matched!")
			return ([],[])
		return (books_name,books_url)

	def choose_book(self,books_name,books_url):  #返回选择的书的目录栏url
		if len(books_name)==1:
			self.book_name=books_name[0][0]
			self.author=books_name[0][1]
			return books_url[0]
			#self.get_book(books_url[0])
		else:
			sn=1
			table=PrettyTable()
			table.field_names=["Serial Number","book name","author"]
			for i in books_name:
				row=[sn]
				row.extend(i)
				table.add_row(row)
				#print(sn,".",i)
				sn+=1
			print(table)
			paurl=1
			while True:
				paurl=input("Please enter the book serial number that needs to be downloaded\n")
				if not paurl:
					paurl=1
				else:
					paurl=int(paurl)
				confirm=input("Are you sure you want to download this book?(y/n)Or input 'exit' to leave\n{}\n".format(books_name[paurl-1])) or "y"
				if confirm=='y':
					self.book_name=books_name[paurl-1][0]
					self.author=books_name[paurl-1][1]
					break
				if confirm=='exit':
					sys.exit()
			return books_url[paurl-1]
			#self.get_book(books_url[paurl-1])

	def get_download_url(self,target):  #返回章节目录数
		req=super().class_request(target)
		req.encoding='utf-8'
		html=req.text
		li_bf=BeautifulSoup(html, "lxml")
		dt_tag=li_bf.find('dt',string=re.compile(r'《.+》正文'))
		dds=dt_tag.find_next_siblings('dd')
		nums=len(dds)
		for i in dds:
			a_bf=BeautifulSoup(str(i),'lxml')
			a=a_bf.find_all('a') 
			self.title.append(a[0].string) # a下面的string可以返回所有框内的值，获取章节名
			path=self.server+a[0].get('href') #获取"href"属性的值，即链接
			self.urls.append(path)#将链接放入urls列表
		return nums

	def get_contents(self,target):
		req=super().class_request(target)
		req.encoding='utf-8'
		html=req.text
		bf=BeautifulSoup(html,'lxml') 
		div=bf.find_all('div',id=self.content_tag)
		txt=''
		try:
			for node in div[0].contents[1:-1]: #去除头尾广告
				content=node.text
				if not content and self.whether_epub==False: #如果content是空字符串
					content='\n'
				elif not content and self.whether_epub==True:
					content='<br>'
				txt+=content
		except:
			print("erro","-"*50)
			print(html)
		next_p=bf.find_all('div',class_=self.change_class)
		# print(next_p)
		target=target.replace(".html","") #用于统一格式
		target+="_1"
		target+=".html"
		while "下一页" in next_p[0].text:
			# print("there is it")
			page=int(re.findall(r"_(\d+)\.html",target)[0])+1
			# print("page is ",page)
			tmp="_{}.html".format(str(page))
			target=re.sub(r'_(\d+)\.html', tmp, target)
			#print("target is ",target)
			req=super().class_request(target)
			req.encoding='utf-8'
			html=req.text
			bf=BeautifulSoup(html,'lxml')
			div=bf.find_all('div',id=self.content_tag)
			# print("text is ",div[0].text)
			try:
				for node in div[0].contents[1:-1]: #去除头尾的网址广告
					content=node.text
					if not content and self.whether_epub==False: #如果content是空字符串
						content='\n'
					elif not content and self.whether_epub==True:
						content='<br>'
					txt+=content
			except:
				print("erro","-"*50)
				print(html)
				print(target)
			next_p=bf.find_all('div', class_=self.change_class)
			# print(next_p)
		# print(txt)
		return txt

	def crawl_book(self,url):
		nums=self.get_download_url(url)
		#print(url)
		print('Start downloading the main body')
		print('there are ',nums,' chapters.')
		try:
			os.mkdir(self._workfile_path)  #创建一个工作目录
		except:  #清空工作目录
			for file_name in os.listdir(self._workfile_path):
				file_path = os.path.join(self._workfile_path,file_name)
				# 如果是文件，则删除
				if os.path.isfile(file_path):
					os.remove(file_path)
		if self.whether_epub==False:
			book_txt_name=self.book_name+".txt"
			with open(basic_path+"\\"+book_txt_name, 'w', encoding='utf-8') as f:  #清空已有文件
				pass
		with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
			all_task=[executor.submit(super(Get_Book_35,self).writer,self.title[i],self.book_name+"_"+str(i)+".txt",self.urls[i]) for i in range(nums)]
			with Progress() as progress:
				task=progress.add_task("[cyan]Processing...", total=100)
				for future in as_completed(all_task):
					future.add_done_callback(super().call_back)
					progress.update(task,advance=(100/nums))
				progress.update(task,completed=100)
		#开始整合
		super().integrate(nums,url,True)
		os.rmdir(self._workfile_path)  #删除工作目录
		print("Total timeout retransmitted for ",self.sleep_time,"times")
		print('下载完成')
		print("————————END————————")

	def run(self):  #主程序
		books_name,books_url=self.search_book()
		if len(books_name)==0:
			sys.exit()
		url=self.choose_book(books_name,books_url)
		self.crawl_book(url)
	

class Get_Book_dingdian(Get_Book):
	def __init__(self,book_name,whether_epub,whether_Proxies,whether_register,num,thread_num,proxy_pool=None): #是否使用代理，代理池大小
		super().__init__(book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool)
		self.server="https://www.txt263.com" #www.023zw.com
		self.headers={
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
		"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
		"Accept-Encoding": "gzip, deflate",
		"Upgrade-Insecure-Requests": "1",
		"Sec-Fetch-Dest": "document",
		"Sec-Fetch-Mode": "navigate",
		"Sec-Fetch-Site": "none",
		"Sec-Fetch-User": "?1",
		"Priority": "u=0, i",
		"Te": "trailers",
		"Connection": "close"
		}  #目标的请求头，用来说明服务器使用的附加信息
		self.content_tag="word_read"
		self.picture_tag='imgbox'
		self.chapter_num=None
		self.whether_register=whether_register

	def download_image(self,url,path,header=None): #重写加入headers
		try:
			response=requests.get(url,headers=header,verify=not host_agent)
			response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常
			#print(response.elapsed.total_seconds())
			#print('get response')
			with open(path, 'wb') as file:
				file.write(response.content)
		except requests.exceptions.RequestException as e:
			print("erro!","-"*50)
			print(e)
			sys.exit()
		return response.headers

	def ver_code(self,picture): #验证码识别
		image=cv.imread(picture)
		resized_image=cv.resize(image, None, fx=3.0, fy=3.0, interpolation=cv.INTER_LINEAR)
		# 边缘保留滤波  去噪
		dst = cv.pyrMeanShiftFiltering(resized_image, sp=10, sr=70)
		# 灰度图像
		gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
		# 二值化
		ret, binary = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
		# 形态学操作   腐蚀  膨胀
		kernel = np.ones((5,5), dtype=np.uint8)
		erode = cv.erode(binary, kernel, iterations=1) #30 30 4
		kernel = np.ones((3,3), dtype=np.uint8)
		dilate = cv.dilate(erode, kernel, iterations=1)
		# 识别
		test_message = Images.fromarray(dilate)
		#test_message.save("test.png")
		text=mypytesseract.image_to_string(test_message)  #,lang="eng"
		text=''.join(filter(str.isalnum,text))
		if len(text)==4:
			return text
		else:
			return None

	def get_code_cookie(self): #获取验证码内容以及对应的cookie
		impath=basic_path+'\\code.jpg'
		cookie=None
		new_header=self.headers
		new_header["authority"]='www.txt263.com'
		for j in range(10): #设置最大循环次数
			header=self.download_image(self.server+"/code.jpg?"+str(random.random()),impath,new_header) #50.118.164.201
			try:
				cookie=header['Set-Cookie'].split(';')[0]
				break
			except:
				os.remove(impath)
		else:
			print("Can't get the cookie!")
			sys.exit()
		codes=self.ver_code(impath)
		if codes==None: #验证码识别出错
			os.remove(impath)
			return (None,None)
		#print(codes)
		os.remove(impath)
		return (cookie,codes)

	def log_in(self):
		print('The program is currently logging in……')
		account=[("woshixiaozhao","123_bruce"),
				("woshixiaozhao2","1234_bruce"),
				("woshixiaozhao3","12345_bruce"),
				("woshixiaozhao4","123456_bruce"),
				("woshixiaozhao5","123457_bruce"),
				("woshixiaozhao6","1234578_bruce")]  #初始账户密码
		#super().request(self.server+"login.html")
		req=None
		with Progress() as progress:
			task=progress.add_task("[cyan]Processing...", total=100)
			for i in range(15): #设置最大循环次数 
				cookie,codes=self.get_code_cookie()
				if cookie==None:
					continue
				new_header=self.headers
				new_header["Cookie"]=cookie
				ranum=random.randint(0,5) #随机登陆一个账户
				user_name=account[ranum][0]
				md5_hash = hashlib.md5() #密码进行hash运算
				md5_hash.update(account[ranum][1].encode('utf-8'))
				md5_result = md5_hash.hexdigest()
				user_pass=md5_result
				data={"user_name":user_name,"user_pass":user_pass,"user_code":codes}
				req=requests.post(self.server+"/qs_login_go.php",data=data,headers=new_header)
				req.encoding='utf-8'
				res_list=req.text.split('|')
				progress.update(task, advance=6.6)
				if res_list[0]=="1":
					progress.update(task,completed=100)
					break
			else:
				print("Verification code recognition module error")
				return None
		tmplist=req.headers['Set-Cookie'].split(';')
		cookie_login=tmplist[0]+";"+tmplist[2].split(',')[1]+";"+tmplist[4].split(',')[1]
		return cookie_login

	def register(self): #需要判断返回值
		print('The program is currently registering and logging in……')
		phone_num_head=[133,142,144,146,148,149,153,180,181,189,130,131,132,141,143,145,155,156,185,186,134,135,136,137,138,139,140,147,150,151,152,157,158,159,182,183,187,188] #标准格式
		req=None
		characters=string.ascii_letters  # 包含所有字母 (大写和小写)
		user_name=''.join(random.choices(characters, k=14))
		md5_hash=hashlib.md5() #密码进行hash运算
		md5_hash.update(''.join(random.choices(characters, k=7)).encode('utf-8'))
		md5_result=md5_hash.hexdigest()
		user_pass=md5_result
		mobile=str(phone_num_head[random.randint(0,len(phone_num_head)-1)])+str(random.randint(10000000, 99999999)) #生成电话号码
		with Progress() as progress:
			task=progress.add_task("[cyan]Processing...", total=100)
			for i in range(15): #设置最大循环次数
				cookie,codes=self.get_code_cookie()
				if codes==None:
					continue
				new_header=self.headers
				new_header["Cookie"]=cookie
				data={"name":user_name,"mobile":mobile,"pass":user_pass,"pass2":user_pass,"code":codes}
				req=requests.post(self.server+"/qs_register_go.php",data=data,headers=new_header)
				req.encoding='utf-8'
				res_list=req.text.split('|')
				progress.update(task, advance=6.6)
				if res_list[0]=="1" and 'Set-Cookie' not in req.headers:
					progress.update(task,completed=100)
					return None
				elif res_list[0]=="1":
					progress.update(task,completed=100)
					break
			else:
				print("Verification code recognition module error")
				return None
		tmplist=req.headers['Set-Cookie'].split(';')
		header_login=tmplist[0]+";"+tmplist[2].split(',')[1]+";"+tmplist[4].split(',')[1]
		return header_login
		
	def search_book(self): #返回需要下载数据的目录地址
		#encoded_url=quote(self.book_name)
		url=self.server+"/search.html"
		data={'s':self.book_name}
		req=super().class_request(url,method=True,data=data)
		html=req.text
		books_name=[]
		books_url=[]
		ul_list=BeautifulSoup(html,'lxml')
		ul=ul_list.find_all('ul',class_='txt-list txt-list-row5')
		cato=BeautifulSoup(str(ul),'lxml')
		li=cato.find_all('li')
		for i in li:
			li_cato=BeautifulSoup(str(i),'lxml')
			span=li_cato.find_all('span')
			books_name.append([span[0].string,span[1].string,span[2].string]) #获取书籍分类，书名，作者（注：想要获取字数则添加td[3].string,最后更新时间添加td[4].string）
			s2=li_cato.find_all('a')
			books_url.append(self.server+s2[0].get('href')) 
		if len(books_name)!=len(books_url):
			print("format error")
			sys.exit()
		if len(books_name)==0:
			print("please try again,the keyword is not matched!")
			return ([],[])
		return (books_name,books_url)

	def choose_book(self,books_name,books_url):  #返回选择的书的目录栏url
		if len(books_name)==1:
			self.book_name=books_name[0][1]
			self.author=books_name[0][2]
			return books_url[0]
			#self.get_book(books_url[0])
		else:
			sn=1
			table=PrettyTable()
			table.field_names=["Serial Number","classification","book name","author"]
			for i in books_name:
				row=[sn]
				row.extend(i)
				table.add_row(row)
				#print(sn,".",i)
				sn+=1
			print(table)
			paurl=1
			while True:
				paurl=input("Please enter the book serial number that needs to be downloaded\n")
				if not paurl:
					paurl=1
				else:
					paurl=int(paurl)
				confirm=input("Are you sure you want to download this book?(y/n)Or input 'exit' to leave\n{}\n".format(books_name[paurl-1])) or "y"
				if confirm=='y':
					self.book_name=books_name[paurl-1][1]
					self.author=books_name[paurl-1][2]
					break
				if confirm=='exit':
					sys.exit()
			return books_url[paurl-1]
			#self.get_book(books_url[paurl-1])

	def thread_chapter(self,target,start): #传入本页初始章节数
		req=super().class_request(target)
		req.encoding='utf-8'
		html=req.text
		page=BeautifulSoup(html,'lxml')
		lis=page.find_all('ul',class_='section-list fix ycxsid')
		cha_list=BeautifulSoup(str(lis[0]),'lxml')
		li=cha_list.find_all('li')
		index=start
		for i in li:
			if index>(self.chapter_num-1):
				print('something erro in ',i)
				break
			a_bf=BeautifulSoup(str(i),'lxml')
			a=a_bf.find_all('a') 
			self.title[index]=a[0].string # a下面的string可以返回所有框内的值，获取章节名
			path=self.server+a[0].get('href') #获取"href"属性的值，即链接
			self.urls[index]=path#将链接放入urls列表
			index+=1

	def get_download_url(self,target):  #返回章节目录数
		req=super().class_request(target)
		req.encoding='utf-8'
		html=req.text
		page=BeautifulSoup(html,'lxml')
		layout=page.find_all('div',class_='layout layout-col1')
		cha=BeautifulSoup(str(layout[2]),'lxml') 
		lis=cha.find_all('ul',class_='fix section-list')
		cha_list=BeautifulSoup(str(lis[0]),'lxml')
		li=cha_list.find_all('li')
		for i in li:
			a_bf=BeautifulSoup(str(i),'lxml')
			a=a_bf.find_all('a') 
			self.title.append(a[0].string) # a下面的string可以返回所有框内的值，获取章节名
			path=self.server+a[0].get('href') #获取"href"属性的值，即链接
			self.urls.append(path)#将链接放入urls列表
		next_page=cha.find_all('a',class_='btn-mulu')
		if '查看更多章节...' in next_page[0].string:
			url=self.server+next_page[0].get('href')
			req=super().class_request(url)
			req.encoding='utf-8'
			html=req.text
			page=BeautifulSoup(html,'lxml')
			page_num=page.find_all('div',class_='page_num')  #共有上下两个page_num
			page_list=BeautifulSoup(str(page_num[0]),'lxml')
			options=page_list.find_all('option')
			last_page=options[-1].string #获取最后一页以确定需要的列表None个数
			num_list=re.findall(r'\d+',last_page)
			last_page_chapter=int(num_list[1])-int(num_list[0])+2 #这个网站有点问题，最后一章的章节数少了1
			#print(last_page_chapter)
			page_nums=len(options)-1
			uninitialized_cha_num=(page_nums-1)*100+last_page_chapter
			self.chapter_num=uninitialized_cha_num+100
			self.title+=[None]*uninitialized_cha_num #初始化列表
			self.urls+=[None]*uninitialized_cha_num
			#print(len(self.title))
			if len(options)>3:  #如果页数太多则使用多线程
				with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
					all_task=[executor.submit(self.thread_chapter,self.server+option.get('value'),100+index*100) for index,option in enumerate(options[1:])]
					with Progress() as progress:
						task=progress.add_task("[cyan]Processing...", total=100)
						for future in as_completed(all_task):
							future.add_done_callback(super().call_back)
							progress.update(task,advance=(100/page_nums))
						progress.update(task,completed=100)
			else:
				for index,option in enumerate(options[1:]):
					self.thread_chapter(self.server+option.get('value'),100+index*100)

	def page_content(self,html,txt):
		bf=BeautifulSoup(html,'lxml') 
		div=bf.find_all('div',class_=self.content_tag)
		ps=BeautifulSoup(str(div[0]),'lxml')
		scripts=ps.find_all('script')
		#print(scripts)
		for script in scripts: 
			if self.whether_epub==False:
				content=re.search("\'(.+)\'",script.contents[0]).group(1).encode('utf-8')
				content=base64.b64decode(content).decode('utf-8')
				content=re.search("<p>(.+)</p>",content).group(1)+'\n\n'
			elif self.whether_epub==True:
				content=re.search("\'(.+)\'",script.contents[0]).group(1).encode('utf-8')
				content=base64.b64decode(content).decode('utf-8')
			txt+=content
		tag=BeautifulSoup(str(ps.find_all('div',class_='read_btn')[0]),'lxml')
		urln=tag.find_all('a')[3].get('href')
		if re.search(r"(_\d+)",urln)==None:
			return (txt,False)
		else:
			return (txt,True)

	def get_contents(self,target):
		target=target.replace(".html","") #用于统一格式
		target+="_0.html"
		txt=''
		while True:
			req=super().class_request(target)
			req.encoding='utf-8'
			html=req.text
			txt,whether_next=self.page_content(html,txt)
			if whether_next==False:
				break
			page=int(re.findall(r"_(\d+)\.html",target)[0])+1
			tmp="_{}.html".format(str(page))
			target=re.sub(r'_(\d+)\.html', tmp, target)
		return txt

	def crawl_book(self,url):  #爬取书籍部分
		print('Downloading directory')
		self.get_download_url(url)
		print('Start downloading the main body')
		print('there are ',self.chapter_num,' chapters.')
		try:
			os.mkdir(self._workfile_path)  #创建一个工作目录
		except:  #清空工作目录
			for file_name in os.listdir(self._workfile_path):
				file_path = os.path.join(self._workfile_path,file_name)
				# 如果是文件，则删除
				if os.path.isfile(file_path):
					os.remove(file_path)
		if self.whether_epub==False:
			book_txt_name=self.book_name+".txt"
			with open(basic_path+"\\"+book_txt_name, 'w', encoding='utf-8') as f:  #清空已有文件
				pass
		with ThreadPoolExecutor(max_workers=self.thread_num) as executor:
			all_task=[executor.submit(super(Get_Book_dingdian,self).writer,self.title[i],self.book_name+"_"+str(i)+".txt",self.urls[i]) for i in range(self.chapter_num)]
			with Progress() as progress:
				task=progress.add_task("[cyan]Processing...", total=100)
				for future in as_completed(all_task):
					future.add_done_callback(super().call_back)
					progress.update(task,advance=(100/self.chapter_num))
				progress.update(task,completed=100)
		#开始整合
		super().integrate(self.chapter_num,url,False)
		os.rmdir(self._workfile_path)  #删除工作目录
		print("Total timeout retransmitted for ",self.sleep_time,"times")
		print('Download completed')
		print("————————END————————")

	def main_login(self): #负责获得cookie 
		cookie=None
		for i in range(3):
			if self.whether_register==True:
				cookie=self.register()
			else:
				cookie=self.log_in()
			if cookie!=None:
				break
		else:
			print("It seems that the verification program has indeed encountered significant errors. Please contact the author!")
			sys.exit()
		print("logged in successfully……")
		self.headers['Cookie']=cookie

	def run(self):  #主程序
		self.main_login()
		books_name,books_url=self.search_book()
		if len(books_name)==0:
			print("sorry,the book can't be found in dingdian net!")
			sys.exit()
		url=self.choose_book(books_name,books_url)
		self.crawl_book(url)

def input_bookname():
	print("book crawler is opened……")
	get_book_name=input("Please enter the name of the book you want to crawl\n")
	return get_book_name

def get_book_main(book_name,whether_epub,whether_Proxies,whether_register,num,thread_num):
	book_35=Get_Book_35(book_name,whether_epub,whether_Proxies,num,thread_num)
	book_dingdian=Get_Book_dingdian(book_name,whether_epub,whether_Proxies,whether_register,num,thread_num,book_35.proxies_pool)
	book_dingdian.main_login()
	books_name_35,books_url_35=book_35.search_book()
	books_name_dingdian,books_url_dingdian=book_dingdian.search_book()
	website=None
	len_35=len(books_name_35)
	len_dingdian=len(books_name_dingdian)
	if len_35+len_dingdian==1:
		if len_35==1: #使用35
			book_35.book_name=books_name_35[0][0]
			book_35.author=books_name_35[0][1]
			ul_url=books_url_35[0]
			book_35.crawl_book(ul_url)
		else: #使用顶点
			book_dingdian.book_name=books_name_dingdian[0][1]
			book_dingdian.author=books_name_dingdian[0][2]
			ul_url=books_url_dingdian[0]
			book_dingdian.crawl_book(ul_url)
	else:
		sn=1
		table=PrettyTable()
		table.field_names=["Serial Number","Referer","classification","book name","author"]
		for i,element in enumerate(books_name_35):
			element.insert(0,i) #包存初始序列
			element.insert(1,"35小说网")
			element.insert(2,"")
		for i,element in enumerate(books_name_dingdian):
			element.insert(0,i)
			element.insert(1,"顶点小说")
		bookname=books_name_dingdian+books_name_35 #合并名字列表，如果优先级为35小说则调换顺序
		bookname_down=[] #用于存储已经出现过的书名
		to_delete=[]
		for i,element in enumerate(bookname):
			new_name=element[3]
			if i<len_dingdian:
				bookname_down.append(new_name)
			elif new_name not in bookname_down:
				bookname_down.append(new_name)
			else:
				to_delete.append(i) #防止重复
				continue
			row=[sn]
			row.extend(element[1:])
			table.add_row(row)
			sn+=1
		del bookname_down
		for i in reversed(to_delete):
			del bookname[i]
		print(table)
		paurl=1
		while True:
			paurl=input("Please enter the book serial number that needs to be downloaded\n")
			if not paurl:
				paurl=1
			else:
				paurl=int(paurl)
			confirm=input("Are you sure you want to download this book?(y/n)Or input 'exit' to leave\n{}\n".format(bookname[paurl-1][1:])) or "y"
			if confirm=='y':
				if bookname[paurl-1][1]=='35小说网':				
					book_35.book_name=bookname[paurl-1][3]
					book_35.author=bookname[paurl-1][4]
					index=bookname[paurl-1][0]
					#print("35",books_url_35[index])
					#print(books_name_35[index])
					book_35.crawl_book(books_url_35[index])
				else:
					book_dingdian.book_name=bookname[paurl-1][3]
					book_dingdian.author=bookname[paurl-1][4]
					index=bookname[paurl-1][0]
					#print("dingdian",books_url_dingdian[index])
					#print(books_name_dingdian[index])
					book_dingdian.crawl_book(books_url_dingdian[index])
				break
			if confirm=='exit':
				sys.exit()

def validate_single_option(args):
	# 计算被传入的选项数量
	options = [args.n35, args.dingdian, args.compuse]
	num_selected = sum(1 for option in options if option is True)
	if num_selected>1:
		print("Error: you can't choose both two of them,you can use both websites to search for books simultaneously without passing in these two parameters or input --compuse")
		sys.exit()

if __name__ == '__main__':
	parser=argparse.ArgumentParser(description="This is a teaching interface")
	parser.add_argument("-noepub",default=False,action="store_true",help="Not outputting books in EPUB format(output in txt format)")
	parser.add_argument("-noproxies",default=False,action="store_true",help="Not using proxy to crawl books(Default not to use proxy)")
	parser.add_argument("--pps",type=int,default=30,help="Input a int number as the size of proxies pool(Default is 30)")
	parser.add_argument("--tn",type=int,default=168,help="Input a int number as the number of threads(Default is 168)")
	parser.add_argument("--n35",default=False,action="store_true",help="Using only 35 Novel Network to crawl books")
	parser.add_argument("--dingdian",default=False,action="store_true",help="Using only DingDian Novel Network to crawl books")
	parser.add_argument("--compuse",default=False,action="store_true",help="Simultaneously use DingDian Novel Network and 35 Novel Network to obtain books for you to choose from")
	parser.add_argument("--dlogin",default=False,action="store_true",help="Log in directly through default accounts instead of registering a new account (note: there may be a risk of account suspension)")
	args=parser.parse_args()
	validate_single_option(args) #判断是否出错
	if args.n35:
		if args.dlogin:
			print('warning,you cannot specify whether to register, as 35 Novel Network does not require registration!')
		get_book_name=input_bookname()
		book_35=Get_Book_35(get_book_name,not args.noepub,not args.noproxies,args.pps,args.tn) #默认转化为epub，默认不适用代理
		book_35.run()
	else:
		mypytesseract=importlib.import_module('pytesseract') #导入需要的模块
		Images=getattr(importlib.import_module('PIL'),'Image')
		np=importlib.import_module('numpy')
		cv=importlib.import_module('cv2')
		if args.dingdian:
			get_book_name=input_bookname()
			book_dingdian=Get_Book_dingdian(get_book_name,not args.noepub,not args.noproxies,not args.dlogin,args.pps,args.tn)
			book_dingdian.run()
		else:
			get_book_name=input_bookname()
			get_book_main(get_book_name,not args.noepub,not args.noproxies,not args.dlogin,args.pps,args.tn)
