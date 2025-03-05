from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from prettytable import PrettyTable
from urllib.parse import quote
from ebooklib import epub
import requests
import time
import re
import os
import sys
import random
import argparse
import wget

host_agent=False #默认不使用主机代理
##basic_path=r"C:\Users\34119\Desktop\script library\get_book_ul\books"  #存放书籍路径 
current_path = os.path.realpath(__file__)
directory_path = os.path.dirname(current_path)
basic_path = directory_path + '\\books'
os.makedirs(basic_path, exist_ok = True)

class Proxies_Pool:
	def __init__(self):
		self.proxies_pool=[]  #初始化代理池

	def get_Proxies(self,num):  #从github上获取num个代理
		url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"
		wget.download(url)
		with open("http.txt", 'r',encoding='utf-8') as source:
			ip_list=source.readlines()
			ip_list=["http://"+ip.strip() for ip in ip_list]
		os.remove("http.txt")
		self.proxies_pool=ip_list[:num]
		return self.proxies_pool

class Get_Book_35:
	def __init__(self,whether_epub,whether_Proxies,num,thread_num): #是否使用代理，代理池大小
		print("book crawlers is opened……")
		self.book_name=input("Please enter the name of the book you want to crawl\n") 
		self.whether_Proxies=whether_Proxies
		if self.whether_Proxies==True:
			pp=Proxies_Pool()
			self.proxies_pool=pp.get_Proxies(num) #获取代理池
		self.server="https://www.35wx.la"
		self.sleep_time=0 #网页出错次数
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
		self.title=[]
		self.urls=[]
		self._workfile_path=basic_path+r"\workfile"
		self.workfile_path=self._workfile_path+r"\\"
		self.thread_num=thread_num
		self.content_id="ccc"
		self.change_class="bottem2"
		self.whether_epub=whether_epub
		self.author=''
		self.picture_id='fmimg'

	def proxies_request(self,target):  #运用代理下的get请求处理
		global sleep_time
		random_proxies=random.randint(0,len(self.proxies_pool)-1)
		request_time=0
		success=False
		tmp=not host_agent #即默认使用SSL检验
		while success==False:        
			while True:
				try:
					with requests.get(url=target,headers=self.headers,proxies={"http":self.proxies_pool[random_proxies]},timeout=3,verify=tmp) as req:
						success=True
						if req.status_code==200:
							return req
						elif request_time>=5:
							print("-"*20,"network erro!","-"*20)
							sys.exit()
						else:
							time.sleep(1)
					request_time+=1
					sleep_time+=1
				except requests.exceptions.Timeout:  #如果代理不可用
					del self.proxies_pool[random_proxies]
					random_proxies=random.randint(0,len(self.proxies_pool)-1)

	def request(self,target):
		request_time=0
		tmp=not host_agent #即默认使用SSL检验
		while True:
			with requests.get(url=target,headers=self.headers,verify=tmp) as req:
				if req.status_code==200:
					return req
				elif request_time>=5:
					print("-"*20,"network erro!","-"*20)
					sys.exit()
				else:
					time.sleep(1)
			request_time+=1
			sleep_time+=1

	def search_book(self): #返回需要下载数据的目录地址
		encoded_url=quote(self.book_name)
		url="https://www.35wx.la/modules/article/search.php/?searchkey={}&searchtype=articlename".format(encoded_url)
		if self.whether_Proxies==True:
			req=self.proxies_request(url)
		else:
			req=self.request(url)
		html=req.text
		books_name=[]
		books_url=[]
		tr_nr=BeautifulSoup(html,'lxml')
		tr=tr_nr.find_all('tr',id='nr')
		for i in tr:
			td_odd=BeautifulSoup(str(i),'lxml')
			td=td_odd.find_all('td')
			books_name.append([td[0].string,td[2].string,td[5].string]) #获取书名，作者，连载状态（注：想要获取字数则添加td[3].string,最后更新时间添加td[4].string）
			a=td_odd.find_all('a')
			books_url.append(a[0].get('href'))
		if len(books_name)!=len(books_url):
			print("something erro!")
			sys.exit()
		if len(books_name)==0:
			print("please try again,the keyword is not matched!")
			sys.exit()
		if len(books_name)==1:
			self.book_name=books_name[0][0]
			self.author=books_name[0][1]
			return books_url[0]
			#self.get_book(books_url[0])
		else:
			sn=1
			table=PrettyTable()
			table.field_names=["Serial Number","book name","author","status"]
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
		req=self.request(target)
		req.encoding='utf-8'
		html=req.text
		li_bf = BeautifulSoup(html,'lxml') 
		dd=li_bf.find_all('dd') # 找到html代码中所有class=list_main的dd列表标签，保存到名为dd的数组里，注意class一定要在同一个标签中，比如<dd class=***>才可以用class筛选
		nums=len(dd)-9 # 去除最新章节部分
		for i in dd[9:]:
			a_bf=BeautifulSoup(str(i),'lxml')
			a=a_bf.find_all('a') 
			self.title.append(a[0].string) # a下面的string可以返回所有框内的值，获取章节名
			path=self.server+a[0].get('href') #获取"href"属性的值，即链接
			self.urls.append(path)#将链接放入urls列表
		return nums

	def get_contents(self,target):
		if self.whether_Proxies==True:
			req=self.proxies_request(target)
		else:
			req=self.request(target)
		req.encoding='utf-8'
		html=req.text
		# print(html)
		bf=BeautifulSoup(html,'lxml') 
		div=bf.find_all('div',id=self.content_id)
		txt=''
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
			# print("target is ",target)
			if self.whether_Proxies==True:
				req=self.proxies_request(target)
			else:
				req=self.request(target)
			req.encoding='utf-8'
			html=req.text
			bf=BeautifulSoup(html,'lxml')
			div=bf.find_all('div',id=self.content_id)
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

	def writer(self,title,filename,target):
		text=self.get_contents(target)
		with open(self.workfile_path+filename, 'a', encoding='utf-8') as f:
			f.write("<h3>{}</h3><br>".format(title))
			f.writelines(text)
			f.write('<br>'*4)

	def copy_and_delete_tofile(self,source_file, destination_file):
		with open(self.workfile_path+source_file, 'r',encoding='utf-8') as source:
			content=source.read()       
		with open(basic_path+r"\\"+destination_file, 'a',encoding='utf-8') as destination:
			destination.write(content)
		os.remove(self.workfile_path+source_file)

	def copy_and_delete(self,source_file):  
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

	def get_cover_picture(self,target):
		req=self.request(target) #获取图片
		html=req.text
		bf=BeautifulSoup(html,'lxml') 
		div=bf.find_all('div',id=self.picture_id)
		bf=BeautifulSoup(str(div[0]),'lxml')
		pic=bf.find_all('img')
		picture_url=pic[0].get('src')
		self.download_image(self.server+picture_url,self.workfile_path+'cover.jpg')

	def integrate(self,nums,target):
		print("\nStart integrating……")
		if self.whether_epub==False:
			book_txt_name=self.book_name+".txt"
			for i in range(nums):
				txt_name=self.book_name+"_"+str(i)+".txt"
				self.copy_and_delete_tofile(txt_name,book_txt_name)
		else:
			self.get_cover_picture(target) #获取封面
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
			for i in range(nums):
				txt_name=self.book_name+"_"+str(i)
				c.append(epub.EpubHtml(title=self.title[i],file_name=txt_name+".xhtml",lang='zh-CN'))
				c[i].content=self.copy_and_delete(txt_name+".txt")
				book.add_item(c[i])
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

	def run(self):  #主程序
		target=self.search_book()
		nums=self.get_download_url(target)
		print('开始下载：')
		print('there are ',nums,' chapters.')
		print("loading…… ")  #显示进度
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
			all_task=[executor.submit(self.writer,self.title[i],self.book_name+"_"+str(i)+".txt",self.urls[i]) for i in range(nums)]
			chapter=0  #完成章节数
			for future in as_completed(all_task):
				future.add_done_callback(self.call_back)
				print("\r\r\r\r",chapter/nums*100,"%",end='')  #获取完成进度
				chapter+=1 
		#开始整合
		self.integrate(nums,target)
		os.rmdir(self._workfile_path)  #删除工作目录
		print("Total timeout retransmitted for ",self.sleep_time,"times")
		print('下载完成')
		print("————————END————————")


if __name__ == '__main__':
	parser=argparse.ArgumentParser(description="This is a teaching interface")
	parser.add_argument("-noepub",default=False,action="store_true",help="Not outputting books in EPUB format(output in txt format)")
	parser.add_argument("-proxies",default=False,action="store_true",help="Use proxy to crawl books(Default not to use proxy)")
	parser.add_argument("--pps",type=int,default=30,help="input a int number as the size of proxies pool(Default is 30)")
	parser.add_argument("--tn",type=int,default=168,help="input a int number as the number of threads(Default is 168)")
	args=parser.parse_args()
	book=Get_Book_35(not args.noepub,args.proxies,args.pps,args.tn) #默认转化为epub，默认不适用代理
	book.run()
