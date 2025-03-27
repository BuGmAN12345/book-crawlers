import requests
import sys

from source.config import OPTION

host_agent=OPTION["host_agent"] #默认不使用主机代理

class Proxies_Pool:
	def __init__(self):
		self.proxies_pool=[]  #初始化代理池

	def get_Proxies(self,num):  #从github上获取num个代理
		url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"
		for i in range(3): #尝试三次
			try:
				response = requests.get(url,timeout=5,verify=not host_agent)
				response.raise_for_status()  # 如果响应状态码不是 200，会抛出异常
				if response.status_code==200: #如果成功
					break		
			except requests.exceptions.RequestException as e:
				print(e)
		else:
			print("erro,failed to get github,please try again or open your vpn and turn the var 'host_agent' into True!","-"*50)
			sys.exit()
		ip_list=response.text.split('\n')
		ip_list=["http://"+ip.strip() for ip in ip_list]
		#print(ip_list)
		self.proxies_pool=ip_list[:num]
		print('Proxy pool initialization completed')
		return self.proxies_pool