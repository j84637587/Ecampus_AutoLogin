# import requests
import os
import re
import time

from selenium.common.exceptions import TimeoutException

import chrome_helper
import file_util
import logging

import pytesseract as tess
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

logging.basicConfig(level=logging.INFO)

chrome_helper.check_browser_driver_available()  # 檢查 driver

opts = webdriver.ChromeOptions()
opts.add_experimental_option('useAutomationExtension', False)
opts.add_experimental_option('excludeSwitches', ['enable-automation'])

LoginUrl = 'https://e3.nfu.edu.tw/EasyE3P/LMS2/login.aspx'

ini = file_util.INI_object()  # 建立 Ini 物件
UserAct = ini.get('Login', 'Account')
UserPsd = ini.get('Login', 'Password')
tess_location = ini.get('ORC', 'tesseract')
tess_exit = os.path.isfile(tess_location)

if os.path.isfile(tess_location):
    tess.pytesseract.tesseract_cmd = tess_location
    logging.info("tesseract 位置為: " + tess_location)
else:
    logging.warning("未安裝 tesseract 或 Setting.ini 中 tesseract 位置錯誤, 將不處理驗證碼.")
    logging.info("下載安裝 32 bit https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w32-setup-v5.0.0-alpha"
                 ".20200328.exe")
    logging.info("下載安裝 64 bit https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.0-alpha"
                 ".20200328.exe")

print("開啟瀏覽器中(Chrome)...")
driver = webdriver.Chrome(chrome_helper.CHROME_DRIVER_EXE, options=opts)  # 開啟chrome browser
print("瀏覽器開啟完成!")

try:
    driver.get(LoginUrl)
except TimeoutException as ex:
    logging.error(ex.Message)
    os.system("pause")
    exit(-1)

image_captcha_Path = 'capture.png'
image_Id = 'imgCheck'
image_Path = 'Capture.png'


def get_captcha(driver, element, path):
    driver.save_screenshot(path)  # 先將目前的 screen 存起來
    location = element.location  # 取得圖片 element 的位置
    size = element.size  # 取得圖片 element 的大小
    left = location['x']  # 決定上下左右邊界
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    image = Image.open(path)  # 將 screen load 至 memory
    image = image.crop((left + 1, top + 1, right - 1, bottom - 1))  # 根據位置剪裁圖片(+-1 去邊框)
    image = image.convert('L')  # 將圖像轉為灰度
    image.save(path, 'png')  # 重新儲存圖片為 png 格式
    return image


# 利用OCR取得識驗證碼

def solve_captcha(image):
    # numbers     \u0030-\u0039
    # upper alpha \u0041-\u005a
    # lower alpha \u0061-\u007a
    # 使用 OCR 辨識驗證碼後去除多餘的字再回傳
    return re.sub(u"([^\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", tess.pytesseract.image_to_string(image))


# 輸入資料到欄位

def sinput(driver, acc, pas, code):
    driver.find_element_by_id('txtLoginId').send_keys(UserAct)  # 帳號輸入欄位
    driver.find_element_by_id('txtLoginPwd').send_keys(UserPsd)  # 密碼輸入欄位
    if tess_exit is True:
        driver.find_element_by_id('txtCheck').send_keys(code)
        driver.find_element_by_id('txtCheck').send_keys(Keys.ENTER)  # 驗證碼輸入欄位


# 取得驗證碼圖片;可利用 request 取得圖片

def getCaptchaPNG():
    logging.info('擷取驗證碼中....')
    img = get_captcha(driver, driver.find_element_by_id(image_Id), image_Path)
    logging.info('辨識驗證碼中....')
    return solve_captcha(img)


if tess_exit is True:
    code = getCaptchaPNG()
    while len(code) != 4:
        driver.find_element_by_id('btnCheck').click()  # 重新產生驗證碼
        time.sleep(2)  # 等待延遲
        getCaptchaPNG()
    logging.info('驗證碼為: ', code)
else:
    code = ""

sinput(driver, UserAct, UserPsd, code)
