from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
import re
import os
import sys
import random
import wget

target = 'https://www.35wx.la/0_140141/'#目标网址
server = 'https://www.35wx.la'
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}  #目标的请求头，用来说明服务器使用的附加信息
thread_num=128 #线程数，经过测试128已经开始吃力了
book_name="《请叫我鬼差大人》"
content_id="ccc"
change_class="bottem2"
basic_path=r"C:\Users\34196\Desktop\script library\books"
_workfile_path=basic_path+r"\workfile"
workfile_path=_workfile_path+r"\\"

host_agent=False #默认不使用主机代理

sleep_time=0  #记录网络中断次数

Proxies_Pool=["http://195.35.3.117:80"
,"http://45.95.203.159:4444"
,"http://162.245.85.220:80"
,"http://62.72.56.132:80"
,"http://154.16.146.46:80"
,"http://72.10.160.90:19575"
,"http://45.95.203.167:4444"
,"http://41.89.16.6:80"
,"http://45.90.218.210:4444"
,"http://12.186.205.123:80"
,"http://152.32.243.60:8081"
,"http://117.250.3.58:8080"
,"http://178.48.68.61:18080"
,"http://45.95.203.150:4444"
,"http://45.95.203.109:4444"
,"http://152.101.73.180:13579"
,"http://67.43.227.227:24581"
,"http://203.161.52.193:80"]   #默认代理池

def get_Proxies(num):  #获取代理个数
    global Proxies_Pool
    url="https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/master/http.txt"
    wget.download(url)
    with open("http.txt", 'r',encoding='utf-8') as source:
        ip_list=source.readlines()
        ip_list=["http://"+ip.strip() for ip in ip_list]
    os.remove("http.txt")
    Proxies_Pool=ip_list[:num]

def copy_and_delete(source_file, destination_file):  
        with open(workfile_path+source_file, 'r',encoding='utf-8') as source:
            content = source.read()       
        with open(basic_path+r"\\"+destination_file, 'a',encoding='utf-8') as destination:
            destination.write(content)
        os.remove(workfile_path+source_file)

def integrate(nums):
    print("\nStart integrating……")
    book_txt_name=book_name+".txt"
    for i in range(nums):
        txt_name=book_name+"_"+str(i)+".txt"
        copy_and_delete(txt_name,book_txt_name)

def writer(title, filename, target):
    text=get_contents(target)
    with open(workfile_path+filename, 'a', encoding='utf-8') as f:
        f.write(title + '\n')
        f.writelines(text)
        f.write('\n\n\n\n')

def get_download_url(target,server,title,urls):  
    req = requests.get(url = target,headers = headers)
    if req.status_code != 200:
        time.sleep(1)
        sleep_time+=1
        req = requests.get(url = target,headers = headers)
    html = req.text
    li_bf = BeautifulSoup(html,'lxml') 
    dd = li_bf.find_all('dd') # 找到html代码中所有class=list_main的dd列表标签，保存到名为dd的数组里，注意class一定要在同一个标签中，比如<dd class=***>才可以用class筛选
    nums = len(dd)-9 # 去除最新章节部分
    for i in dd[9:]:
        a_bf = BeautifulSoup(str(i),'lxml')
        a = a_bf.find_all('a') 
        title.append(a[0].string) # a下面的string可以返回所有框内的值，获取章节名
        path = server + a[0].get('href') #获取"href"属性的值，即链接
        '''path=path.replace(".html","")
        path+="_1"
        path+=".html"  #加入_1'''
        urls.append(path)#将链接放入urls列表
    return nums

def proxies_request(target):  #运用代理下的get请求处理
    global sleep_time
    random_proxies=random.randint(0,len(Proxies_Pool)-1)
    request_time=0
    success=False
    tmp=not host_agent #即默认使用SSL检验
    while success==False:        
        while True:
            try:
                with requests.get(url=target,headers=headers,proxies={"http":Proxies_Pool[random_proxies]},timeout=3,verify=tmp) as req:
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
                del Proxies_Pool[random_proxies]
                random_proxies=random.randint(0,len(Proxies_Pool)-1)

def request(target):
    global sleep_time
    request_time=0
    tmp=not host_agent #即默认使用SSL检验
    while True:
        with requests.get(url = target,headers = headers,verify=tmp) as req:
            if req.status_code==200:
                return req
            elif request_time>=5:
                print("-"*20,"network erro!","-"*20)
                sys.exit()
            else:
                time.sleep(1)
        request_time+=1
        sleep_time+=1

def get_contents(target):
    if whether_Proxies==True:
        req=proxies_request(target)
    else:
        req=request(target)
    req.encoding = 'utf-8'
    html = req.text
    # print(html)
    bf=BeautifulSoup(html,'lxml') 
    div=bf.find_all('div', id = content_id)
    txt = ''
    try:
        txt=div[0].text
    except:
        print("erro","-"*50)
        print(html)
    next_p=bf.find_all('div', class_=change_class)
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
        if whether_Proxies==True:
            req=proxies_request(target)
        else:
            req=request(target)
        req.encoding = 'utf-8'
        html = req.text
        bf = BeautifulSoup(html,'lxml')
        div = bf.find_all('div', id = content_id)
        # print("text is ",div[0].text)
        try:
            txt+=div[0].text
        except:
            print("erro","-"*50)
            print(html)
            print(target)
        next_p=bf.find_all('div', class_=change_class)
        # print(next_p)
    # print(txt)
    return txt

def get_book():   #默认不使用代理  
    #主程序   
    title=[]
    urls=[]
    nums=get_download_url(target,server,title,urls)
    print('开始下载：')
    print('there are ',nums,' chapters.')
    print("loading…… ")  #显示进度
    try:
        os.mkdir(_workfile_path)  #创建一个工作目录
    except:  #清空工作目录
        for file_name in os.listdir(_workfile_path):
            file_path = os.path.join(_workfile_path, file_name)
            # 如果是文件，则删除
            if os.path.isfile(file_path):
                os.remove(file_path)
    book_txt_name=book_name+".txt"
    with open(basic_path+"\\"+book_txt_name, 'w', encoding='utf-8') as f:  #清空已有文件
        pass
    executor=ThreadPoolExecutor(max_workers=thread_num)
    all_task=[executor.submit(writer,title[i],book_name+"_"+str(i)+".txt",urls[i]) for i in range(nums)]
    chapter=0  #完成章节数
    for future in as_completed(all_task):
        print("\r\r\r\r",chapter/nums*100,"%",end='')  #获取完成进度
        chapter+=1 
    #开始整合
    # print(Proxies_Pool)
    integrate(nums)
    os.rmdir(_workfile_path)  #删除工作目录
    print("Total timeout retransmitted for ",sleep_time,"times")
    print('下载完成')
    print("————————END————————")


if __name__ == '__main__':
    argc=len(sys.argv)
    if argc>1:
        if sys.argv[1].lower()=="true":  #由于python传参只能传入字符串
            whether_Proxies=True
        else:
            whether_Proxies=False
        if whether_Proxies==True:
            print("Proxies_Pool opened……")
            get_Proxies(30)
        else:
            print("not using proxy server……")
        get_book()
    else:
        whether_Proxies=False #默认不使用代理
        get_book()


