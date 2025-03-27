import os
import random

class Header: #用于管理headers
	def __init__(self,header=None):
		self.headers=header

	def perm_add_header(self,key,value): #添加永久header
		if key in self.headers:
			self.headers[key]=self.headers[key]+";"+value
		else:
			self.headers[key]=value

	def temp_add_header(self,key,value):
		if key in self.headers:
			new_header=self.headers
			new_header[key]=new_header[key]+";"+value
			return new_header
		else:
			new_header=self.headers
			new_header[key]=value
			return new_header

	def perm_replace_header(self,key,value):
		if key in self.headers:
			self.headers[key]=value
		else:
			print("You don't have an initial value for replacement")

	def get_header(self):
		return self.headers

class User_Agent: #用于管理user_agent
	def generate_user_agent(self,browser,os,browser_version):
		if browser==0:
			user_agent=f"Mozilla/5.0 ({os}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser_version} Safari/537.36"
		elif browser==1:
			user_agent=f"Mozilla/5.0 ({os}; rv:{browser_version}) Gecko/20100101 Firefox/{browser_version}"
		else:
			raise ValueError("Unsupported browser")   
		return user_agent

	def rgua(self): #随机生成一个user_agent
		browser=random.randint(0,1)
		os=['Windows NT 10.0; Win64; x64','Linux; Ubuntu 20.04; x86_64','Macintosh; Intel Mac OS X 10_15_7']
		if browser==0:
			return self.generate_user_agent(browser,os[random.randint(0,2)],'{}.0.0.0'.format(random.randint(100,128)))
		if browser==1:
			return self.generate_user_agent(browser,os[random.randint(0,2)],'{}.0'.format(random.randint(100,128)))

