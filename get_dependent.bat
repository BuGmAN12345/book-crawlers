@echo off
setlocal enabledelayedexpansion

pip install --upgrade pip
::Beautifulsoup
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ beautifulsoup4
::concurrent.futures
for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)"') do set "python_version=%%i"
if !python_version! lss 3 (
    pip install futures
)
::prettytable
pip install prettytable
::rich
pip install rich
::base64
pip install base64
::ebooklib
pip install EbookLib
::requests
pip install requests
::wget
pip install wget