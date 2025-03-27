from source.com_get_book import get_book_main
from source.Get_Book_35 import Get_Book_35
from source.Get_Book_dingdian import Get_Book_dingdian

import sys
import argparse
import importlib

from source.config import OPTION

host_agent=OPTION["host_agent"] #默认不使用主机代理
basic_path=OPTION["basic_path"]  #存放书籍路径 

def input_bookname():
	print("book crawler is opened……")
	get_book_name=input("Please enter the name of the book you want to crawl\n")
	return get_book_name

def validate_single_option(args):
	# 计算被传入的选项数量
	if args.getcookie==False and args.dlogin==True:
		print("Erro: If you have chosen not to use cookies, then there is no need to log in or sign up!")
		sys.exit()
	options = [args.n35, args.dingdian, args.compuse]
	num_selected = sum(1 for option in options if option is True)
	if num_selected>1:
		print("Error: you can't choose both two of them,you can use both websites to search for books simultaneously without passing in these two parameters or input --compuse")
		sys.exit()

if __name__ == '__main__':
	parser=argparse.ArgumentParser(description="This is a teaching interface\n")
	parser.add_argument("--noepub",default=False,action="store_true",help="Not outputting books in EPUB format(output in txt format)")
	parser.add_argument("--noproxies",default=False,action="store_true",help="Not using proxy to crawl books(Default not to use proxy)")
	parser.add_argument("--pps",type=int,default=30,help="Input a int number as the size of proxies pool(Default is 30)")
	parser.add_argument("--tn",type=int,default=168,help="Input a int number as the number of threads(Default is 168)")
	parser.add_argument("--n35",default=False,action="store_true",help="Using only 35 Novel Network to crawl books")
	parser.add_argument("--dingdian",default=False,action="store_true",help="Using only DingDian Novel Network to crawl books")
	parser.add_argument("--compuse",default=False,action="store_true",help="Simultaneously use DingDian Novel Network and 35 Novel Network to obtain books for you to choose from")
	parser.add_argument("--dlogin",default=False,action="store_true",help="Log in directly through default accounts instead of registering a new account (note: there may be a risk of account suspension)")
	parser.add_argument("--getcookie",default=False,action="store_true",help="Due to the problems with the login interface of dingdian, it is not necessary to use the login for the time being, please try not to use this parameter")
	args=parser.parse_args()
	validate_single_option(args) #判断是否出错
	if args.n35:
		if args.dlogin:
			print('warning,you cannot specify whether to register, as 35 Novel Network does not require registration!')
		get_book_name=input_bookname()
		book_35=Get_Book_35(get_book_name,not args.noepub,not args.noproxies,args.pps,args.tn) #默认转化为epub，默认不适用代理
		book_35.run()
	else:
		Images=getattr(importlib.import_module('PIL.Image'),'Image')
		pipeline=getattr(importlib.import_module('modelscope.pipelines'),'pipeline')
		Tasks=getattr(importlib.import_module('modelscope.utils.constant'),'Tasks')
		np=importlib.import_module('numpy')
		cv=importlib.import_module('cv2')
		if args.dingdian:
			get_book_name=input_bookname()
			book_dingdian=Get_Book_dingdian(get_book_name,not args.noepub,not args.noproxies,not args.dlogin,args.pps,args.tn,args.getcookie)
			book_dingdian.run()
		else:
			get_book_name=input_bookname()
			get_book_main(get_book_name,not args.noepub,not args.noproxies,not args.dlogin,args.pps,args.tn,args.getcookie)
