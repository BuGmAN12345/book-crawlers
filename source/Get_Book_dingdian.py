from source.Header import Header
from source.basic_class_function import Get_Book

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from prettytable import PrettyTable
from rich.progress import Progress
import base64
import requests
import hashlib
import string
import re
import os
import sys
import random

from source.config import OPTION

host_agent=OPTION["host_agent"] #默认不使用主机代理
basic_path=OPTION["basic_path"]  #存放书籍路径 

class Get_Book_dingdian(Get_Book):
	def __init__(self,book_name,whether_epub,whether_Proxies,whether_register,num,thread_num,whether_cookie,proxy_pool=None): #是否使用代理，代理池大小
		super().__init__(book_name,whether_epub,whether_Proxies,num,thread_num,proxy_pool)
		self.server="https://www.txt263.com" #www.023zw.com
		tmp={
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		"Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
		"Accept-Encoding": "gzip, deflate",
		"Upgrade-Insecure-Requests": "1",
		"Sec-Fetch-Dest": "document",
		"Sec-Fetch-Mode": "navigate",
		"Sec-Fetch-Site": "same-origin",
		"Sec-Fetch-User": "?1",
		"Priority": "u=0, i",
		"Te": "trailers",
		}  #目标的请求头，用来说明服务器使用的附加信息
		self.headers=Header(tmp)
		self.content_tag="word_read"
		self.picture_tag='imgbox'
		self.chapter_num=None
		self.whether_register=whether_register
		self.whether_cookie=whether_cookie
		if self.whether_cookie:
			model_small = r"ocr-captcha/output_small"
			self.ocr_recognition_small = pipeline(Tasks.ocr_recognition, model=model_small)

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

	def im_show(self,pic_name,pic):
		cv.imshow(pic_name,pic)
		cv.waitKey(0)
		cv.destroyAllWindows()

	def pic_handle_spe(self,picture): #特异化图片处理
		image=Images.open(picture)  # 替换为你的图片路径
		image=image.convert('RGB')
		pixels=image.load()  # 获取像素数据
		for i in range(image.width):
			for j in range(image.height):
				r, g, b = pixels[i, j]  # 获取当前像素的 RGB 值
				if (r + g + b) > 550 and b >= r and b >= g:
					pixels[i, j]=(0,0,0)  # 满足条件，设为黑点
				else:
					pixels[i, j]=(255,255,255)  # 不满足条件，设为白点
		image= np.array(image)
		image=cv.resize(image, None, fx=3.0, fy=3.0, interpolation=cv.INTER_LINEAR)
		binary=image[:, :, 0]
		kernel = np.ones((5,5), dtype=np.uint8)
		erode = cv.erode(binary, kernel, iterations=1) #30 30 4
		kernel = np.ones((3,3), dtype=np.uint8)
		dilate = cv.dilate(erode, kernel, iterations=1)
		#self.im_show("binary",dilate)
		test_message = Images.fromarray(dilate)
		#test_message.save(basic_path+'\\output_image{}.tiff'.format(random.randint(1,10086)))
		return test_message

	def pic_handle_gen(self,picture): #图像处理
		image=cv.imread(picture)
		resized_image=cv.resize(image, None, fx=3.0, fy=3.0, interpolation=cv.INTER_LINEAR)
		# 边缘保留滤波  去噪
		dst = cv.pyrMeanShiftFiltering(resized_image, sp=10, sr=70)
		# 灰度图像
		gray = cv.cvtColor(dst, cv.COLOR_BGR2GRAY)
		# 二值化
		ret, binary = cv.threshold(gray,0,255,cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
		#self.im_show("binary",binary)
		# 形态学操作   腐蚀  膨胀
		kernel = np.ones((5,5), dtype=np.uint8)
		erode = cv.erode(binary, kernel, iterations=1) #30 30 4
		kernel = np.ones((3,3), dtype=np.uint8)
		dilate = cv.dilate(erode, kernel, iterations=1)
		#self.im_show("dilate",dilate)
		# 识别
		test_message = Images.fromarray(dilate)
		return test_message

	def ver_code(self,picture,is_spe): #验证码识别
		#test_message.save("test.png")
		if is_spe:
			test_message=self.pic_handle_spe(picture)
		else:
			test_message=self.pic_handle_gen(picture)
		result = self.ocr_recognition_small(pict_path)
		text=''.join(filter(str.isalnum,str(result['text'][0])))
		if len(text)==4:
			return text
		else:
			return None

	def get_code_cookie(self,i): #获取验证码内容以及对应的cookie
		impath=basic_path+'\\code{}.jpg'.format(i)
		cookie=None
		new_header=self.headers.temp_add_header("authority",'www.txt263.com')
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
		codes=self.ver_code(impath,False)
		print("codes ",i," is ",codes)
		#print(codes)
		if codes==None: #验证码识别出错
			os.remove(impath)
			return (None,None)
		#print(codes)
		os.remove(impath)
		return (cookie,codes)

	def try_cookie_login(self,account,i): #尝试验证码是否正确 
		cookie,codes=self.get_code_cookie(i)
		if cookie==None:
			return None
		new_header=self.headers.temp_add_header('Cookie',cookie)
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
		if res_list[0]=="1":
			return req
		else:
			return None

	def try_cookie_register(self,i):
		characters=string.ascii_letters  # 包含所有字母 (大写和小写)
		user_name=''.join(random.choices(characters, k=14))
		md5_hash=hashlib.md5() #密码进行hash运算
		md5_hash.update(''.join(random.choices(characters, k=7)).encode('utf-8'))
		md5_result=md5_hash.hexdigest()
		user_pass=md5_result
		mobile=str(phone_num_head[random.randint(0,len(phone_num_head)-1)])+str(random.randint(10000000, 99999999)) #生成电话号码
		cookie,codes=self.get_code_cookie(i)
		if cookie==None:
			return None
		new_header=self.headers.temp_add_header('Cookie',cookie)
		data={"name":user_name,"mobile":mobile,"pass":user_pass,"pass2":user_pass,"code":codes}
		req=requests.post(self.server+"/qs_register_go.php",data=data,headers=new_header)
		req.encoding='utf-8'
		res_list=req.text.split('|')
		progress.update(task, advance=6.6)
		if res_list[0]=="1" and 'Set-Cookie' not in req.headers:
			return None
		elif res_list[0]=="1":
			progress.update(task,completed=100)
			return req

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
		with ThreadPoolExecutor(max_workers=10) as executor:
			all_task=[executor.submit(self.try_cookie_login,account,i) for i in range(30)]
			with Progress() as progress:
				task=progress.add_task("[cyan]Processing...", total=100)
				for future in as_completed(all_task):
					future.add_done_callback(super().call_back)
					progress.update(task,advance=3.3)
					result=future.result()
					#print(result)
					if result is not None: # 如果找到了req，立即终止线程池并返回req
						progress.update(task,completed=100)
						executor.shutdown(wait=False)  # 终止线程池
						req=result
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
		with ThreadPoolExecutor(max_workers=10) as executor:
			all_task=[executor.submit(self.try_cookie_register,i) for i in range(30)]
			with Progress() as progress:
				task=progress.add_task("[cyan]Processing...", total=100)
				for future in as_completed(all_task):
					future.add_done_callback(super().call_back)
					progress.update(task,advance=3.3)
					result=future.result()
					#print(result)
					if result is not None: # 如果找到了req，立即终止线程池并返回req
						progress.update(task,completed=100)
						executor.shutdown(wait=False)  # 终止线程池
						req=result
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
		self.headers.perm_add_header('Cookie',cookie)

	def run(self):  #主程序
		if self.whether_cookie==True:
			self.main_login()
		books_name,books_url=self.search_book()
		if len(books_name)==0:
			print("sorry,the book can't be found in dingdian net!")
			sys.exit()
		url=self.choose_book(books_name,books_url)
		self.crawl_book(url)