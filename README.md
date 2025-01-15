# book-crawlers
## 中文版：
### 很遗憾的是，顶点小说网平台维护出现问题，导致登录无法使用，暂时只能使用35小说网内容
版本更新：

1.1：

更改了request请求的函数，解决了程序出错时socket未关闭的问题，并增加了一个host_agent选项，用于解决当主机网卡使用代理时ssl检验不通过的问题，当
需要使用主机代理时需要修改此全局变量为True

2.1：

更改了整体框架，使用了类方法，可适用于下载35小说网的所有书籍。新程序包含老程序的所有内容，更名为`35_get_book.py`  
在拉取代码后，只需要修改host_agent和basic_path这两个全局变量即可。  
其中host_agent见1.1，basic_path为存放书籍的路径。  
如果需要使用代理（经过验证，35小说网并不需要使用代理），使用  
`python 35_get_book.py True`  
即可，如果不需要直接不传入参数或者传入False即可。默认使用代理池大小为30，线程数为128，可在main位置自行调整  
使用该程序时，先输入需要爬取的书籍关键词，例如:斗罗大陆  
程序返回所有包含关键词的所有书名，作者，状态以及编号，输入最后选定书籍的编号并确认（可以直接回车表示选定第一个书籍，再次回车表示确认）  
注：当搜索关键词不存在时会直接退出程序，搜索关键词只有一本对应书籍时会直接下载  
新增依赖库：  
`pip install prettytable`  

2.2：

新增了输出.epub格式电子书的功能，电子书包括封面+文字封面(书名+作者)+目录+正文部分内容，格式完全与35小说网在线状况相同，并屏蔽了广告。
新增了参数功能，下面是参数帮助：（使用`python 35_get_book.py -h`或`python 35_get_book.py --help`即可获取）  
```
usage: 35_get_book.py [-h] [-noepub] [-proxies] [--pps PPS] [--tn TN]  
This is a teaching interface    
options:  
  -h, --help  show this help message and exit  
  -noepub     Not outputting books in EPUB format(output in txt format)  
  -proxies    Use proxy to crawl books(Default not to use proxy)  
  --pps PPS   input a int number as the size of proxies pool(Default is 30)  
  --tn TN     input a int number as the number of threads(Default is 168)
```

3.1：

新增了爬取顶点小说网的功能，同时开启了同时获取两个小说网相应章节搜索目录，并爬取的功能。注意，也新加入了几个依赖库：（值得注意的是，下面的这几个依赖库只有使用到dingdian小说时才需要配置）
```
import numpy as np
import pytesseract
from PIL import Image
import cv2 as cv
```
为了更美观的显示出进度，新增了如下依赖库：
```
from rich.progress import Progress
```
需要注意的是，爬取顶点小说网需要选择登录方式，即注册或者直接登录，下面是帮助：
```
usage: get_book.py [-h] [-noepub] [-noproxies] [--pps PPS] [--tn TN] [--n35] [--dingdian] [--compuse] [--dlogin]

This is a teaching interface

options:
  -h, --help  show this help message and exit
  -noepub     Not outputting books in EPUB format(output in txt format)
  -noproxies  Not using proxy to crawl books(Default not to use proxy)
  --pps PPS   Input a int number as the size of proxies pool(Default is 30)
  --tn TN     Input a int number as the number of threads(Default is 168)
  --n35       Using only 35 Novel Network to crawl books
  --dingdian  Using only DingDian Novel Network to crawl books
  --compuse   Simultaneously use DingDian Novel Network and 35 Novel Network to obtain books for you to choose from
  --dlogin    Log in directly through default accounts instead of registering a new account (note: there may be a risk
              of account suspension)
```
为了防止配置环境过于复杂，可以使用`get_dependent.bat`来直接获取顶点小说依赖库外的其他所有依赖（因为pytesseract需要手动下载库并配置环境）

### 35_get_book.py
可直接用于爬取35小说网上的所有书籍，并可以转化为epub格式，使用前仅需要提前更改15/16行的内容即可，具体详情请见上方2.1，2.2，输入参数后按照提示选择想要
的书籍爬取即可，速度很快

### get_book.py
情况一：

程序模板可以直接用于下载35小说网的请叫我鬼差大人小说，但在真正运用到本机下载前需要做如下修改：

1.需要将`basic_path`修改为需要的地址

2.需要选择是否使用代理ip池，即向python程序传入True/False（默认不传入参数则为不使用代理池即False）

3.需要依赖库

`pip install wget`

`pip install beautifulsoup4`

`pip install requests`

4.根据电脑情况调整线程数


情况二：

如果需要爬取35小说网的其他小说，只需要修改`target`,`server`并且根据情况适当修改`book_name`,`content_id`,`change_class`等参数


情况三：

如果需要爬取其他小说网，需要修改情况二中的内容并对程序逻辑进行简单修改，后续将会持续更新完善程序使逻辑修改更简洁


### 可能遇到的问题：

1.

使用代理池加载速度比较慢：

可能是因为代理池是从github上面使用wget下载，在中国使用可能不稳定

解决方案：

可以尝试开启vpn再次重试


## English version
### Unfortunately, there is a maintenance issue with the Vertex Novel Network platform, which has resulted in login failure and currently only 35 Novel Network content can be used
Version update:

1.1：  
Changed the function of the request request, solved the problem of socket not being closed when the program encounters an error, and added a host_magent option to solve the problem of SSL verification not passing when the host network card uses a proxy
When using a host agent, it is necessary to modify this global variable to True

2.1：  
Changed the overall framework and used class methods, which can be applied to download all books from 35 Novel Network. The new program contains all the content of the old program and has been renamed as `35_get_book.py`  
After pulling the code, you only need to modify the two global variables host_magent and basic_path.
Among them, host_magent is shown in 1.1, and basic_path is the path to store books.  
If you need to use a proxy (after verification, 35 Novel Network does not require the use of a proxy), use  
`python 35_get_book.py True`  
Okay, if you don't need to pass in any parameters directly or pass in False. The default proxy pool size is 30 and the number of threads is 128, which can be adjusted at the main position  
When using this program, first enter the keywords of the books that need to be crawled, such as "斗罗大陆"  
The program returns all book titles, authors, statuses, and numbers containing keywords. Enter the last selected book number and confirm (you can directly press enter to select the first book, and press enter again to confirm)  
Note: When the search keyword does not exist, the program will exit directly. When there is only one corresponding book for the search keyword, it will be downloaded directly
Add dependency library:  
`pip install prettytable` 

2.2：  
Added the function of outputting. epub format e-books, which include cover+text cover (book title+author)+table of contents+main body content. The format is completely the same as the online status of 35 Novel Network, and advertisements are blocked.  
Added parameter function, below is the parameter help：(using `python 35_get_book.py -h` or `python 35_get_book.py --help` can get it!)  
```
usage: 35_get_book.py [-h] [-noepub] [-proxies] [--pps PPS] [--tn TN]  
This is a teaching interface  
options:  
  -h, --help  show this help message and exit  
  -noepub     Not outputting books in EPUB format(output in txt format)  
  -proxies    Use proxy to crawl books(Default not to use proxy)  
  --pps PPS   input a int number as the size of proxies pool(Default is 30)  
  --tn TN     input a int number as the number of threads(Default is 168)
```

3.1：  
Added the function of crawling vertex novel websites, and also enabled the function of simultaneously obtaining the corresponding chapter search directories of two novel websites and crawling them. Note that several dependency libraries have also been added: (It is worth noting that the following dependency libraries only need to be configured when using Dingdian novels)
```
import numpy as np
import pytesseract
from PIL import Image
import cv2 as cv
```
In order to display progress more visually, the following dependency libraries have been added:
```
from rich.progress import Progress
```
It should be noted that crawling the vertex novel website requires selecting a login method, namely registration or direct login. Here is the help:
```
usage: get_book.py [-h] [-noepub] [-noproxies] [--pps PPS] [--tn TN] [--n35] [--dingdian] [--compuse] [--dlogin]
This is a teaching interface
options:
-h, --help   show this help message and exit
-noepub     Not outputting books in EPUB format(output in txt format)
-noproxies  Not using proxy to crawl books(Default not to use proxy)
--pps PPS   Input a int number as the size of proxies pool(Default is 30)
--tn TN     Input a int number as the number of threads(Default is 168)
--n35        Using only 35 Novel Network to crawl books
--dingdian   Using only DingDian Novel Network to crawl books
--compuse    Simultaneously use DingDian Novel Network and 35 Novel Network to obtain books for you to choose from
--dlogin    Log in directly through default accounts instead of registering a new account (note: there may be a risk
of account suspension)
```
To prevent the configuration environment from being too complex, you can use 'get_dependent. bat' to directly obtain all other dependencies outside the vertex novel dependency library (because pyEsseract requires manually downloading the library and configuring the environment)

### 35_get_book.py  
It can be directly used to crawl all books on the 35 Novel website and can be converted to EPUB format. Before use, only the content of lines 15/16 needs to be changed in advance. For specific details, please refer to sections 2.1 and 2.2 above. After entering the parameters, follow the prompts to select the desired content.Simply crawl the books and it's very fast

### get_book.py  
Scenario 1:

The program template can be directly used to download 35 novels from the website. Please call me Ghost Adventure Adult Novel, but the following modifications need to be made before truly applying it to local downloads:

1. It is necessary to modify `basic_path` to the desired address

2. It is necessary to choose whether to use a proxy IP pool, that is, to pass True/False to the Python program (if no parameters are passed by default, it is False to not use a proxy pool)

3. Dependency library required

`pip install wget`

`pip install beautifulsoup4`

`pip install requests`

4. Adjust the number of threads according to the computer situation


Scenario 2:

If you need to crawl other novels from the 35 Novel Network, simply modify the 'target', 'server', and appropriately modify parameters such as` bookname `,` content_id `, and` change_class` according to the situation


Scenario 3:

If you need to crawl other novel websites, you need to modify the content in situation two and make simple modifications to the program logic. The program will be continuously updated and improved to make the logical modifications more concise


### Possible issues encountered:

1.
The loading speed of using proxy pools is relatively slow:
Perhaps it is because the proxy pool was downloaded from GitHub using wget, which may be unstable when used in China

Solution:

You can try opening VPN and trying again
