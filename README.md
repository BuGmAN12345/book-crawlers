## book-crawlers
# 中文版：

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

# 可能遇到的问题：
1.
使用代理池加载速度比较慢：
可能是因为代理池是从github上面使用wget下载，在中国使用可能不稳定
解决方案：
可以尝试开启vpn再次重试


# 英文版

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
# Possible issues encountered:
1.
The loading speed of using proxy pools is relatively slow:
Perhaps it is because the proxy pool was downloaded from GitHub using wget, which may be unstable when used in China
Solution:
You can try opening VPN and trying again
