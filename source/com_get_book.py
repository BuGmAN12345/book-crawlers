from source.Get_Book_35 import Get_Book_35
from source.Get_Book_dingdian import Get_Book_dingdian

from prettytable import PrettyTable
import sys

def get_book_main(book_name,whether_epub,whether_Proxies,whether_register,num,thread_num,whether_cookie):
	book_35=Get_Book_35(book_name,whether_epub,whether_Proxies,num,thread_num)
	book_dingdian=Get_Book_dingdian(book_name,whether_epub,whether_Proxies,whether_register,num,thread_num,whether_cookie,book_35.proxies_pool)
	if whether_cookie==True:
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
