from source.Header import Header
from source.basic_class_function import Get_Book

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from prettytable import PrettyTable
from rich.progress import Progress
import base64
from urllib.parse import quote
import re
import os
import sys

from source.config import OPTION

host_agent=OPTION["host_agent"] #默认不使用主机代理
basic_path=OPTION["basic_path"]  #存放书籍路径 

class Get_Book_35(Get_Book):
	def __init__(self,book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool=None): #是否使用代理，代理池大小
		#print("book crawlers is opened……")
		super().__init__(book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool)
		self.server="https://www.35wx.la"
		tmp={
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
		self.headers=Header(tmp)
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
	

