#import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pytesseract as tess
from PIL import Image
import time, os,re        #String
import configparser # ini

class INI_object:
    def __init__(self):
        #function:  初始化INI檔案
        cntDir = os.path.split(os.path.realpath(__file__))[0]
        configPath = os.path.join(cntDir, "config.ini")
        # 創建對象
        self.conf = configparser.ConfigParser()
        # 讀取INI
        print("取得帳號, 密碼.")
        self.conf.read(configPath, encoding='utf-8')

    def get(self,section, option):
        #function:  讀取INI檔案配置資訊.
        try:
            ret = self.conf.get(section, option)
            return ret
        except:
            print("不能獲取到%s選項 %s的值. 請確認 congin.ini 是否正確配置?" %(section,option)) 
            os.system("pause")
            exit(1)
    

#r'C:\Users\Quareta\AppData\Local\Tesseract-OCR\tesseract.exe'

opts = webdriver.ChromeOptions()
opts.add_experimental_option('useAutomationExtension', False)
opts.add_experimental_option('excludeSwitches', ['enable-automation'])

ini = INI_object() #初始化 Ini 類別
LoginUrl = 'https://e3.nfu.edu.tw/EasyE3P/LMS2/login.aspx'
UserAct = ini.get('Login', 'Account')
UserPsd = ini.get('Login', 'Password')
tess_location = ini.get('ORC', 'tesseract')
tess_exit = (os.path.exists(tess_location) and os.path.isfile(tess_location))
if tess_exit:
    tess.pytesseract.tesseract_cmd = tess_location
    print("tesseract 位置為: " + tess_location)
else:
    print("未安裝 tesseract 或 Setting.ini 中 tesseract 位置錯誤, 將不處理驗證碼")

image_captcha_Path = 'capture.png'
image_Id = 'imgCheck'
image_Path = 'Capture.png'


print("開啟瀏覽器中(Chrome)...")
driver = webdriver.Chrome(options=opts) #開啟chrome browser
driver.get(LoginUrl)
print("瀏覽器開啟完成!")


def get_captcha(driver, element, path):
    driver.save_screenshot(path)          # 先將目前的 screen 存起來
    location = element.location           # 取得圖片 element 的位置
    size = element.size                   # 取得圖片 element 的大小
    left = location['x']                  # 決定上下左右邊界
    top = location['y']
    right = location['x'] + size['width']
    bottom = location['y'] + size['height']
    image = Image.open(path)              # 將 screen load 至 memory
    image = image.crop((left + 1, top + 1, right - 1, bottom - 1)) # 根據位置剪裁圖片(+-1 去邊框)
    image = image.convert('L')            # 將圖像轉為灰度
    image.save(path, 'png')               # 重新儲存圖片為 png 格式
    return image

def solve_captcha(image):
    code = tess.pytesseract.image_to_string(image)
    code = re.sub(u"([^\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", code)
    # numbers     \u0030-\u0039
    # upper alpha \u0041-\u005a
    # lower alpha \u0061-\u007a
    return code

def sinput(driver, acc, pas, code):
    driver.find_element_by_id('txtLoginId').send_keys(UserAct)   #帳號輸入欄位
    driver.find_element_by_id('txtLoginPwd').send_keys(UserPsd)  #密碼輸入欄位
    if tess_exit == True:
        driver.find_element_by_id('txtCheck').send_keys(code)
        driver.find_element_by_id('txtCheck').send_keys(Keys.ENTER)  #驗證碼輸入欄位

def getCaptchaPNG():
    print("擷取驗證碼中....")
    img = get_captcha(driver, driver.find_element_by_id(image_Id), image_Path)
    print("辨識驗證碼中....")
    code = solve_captcha(img)
    return code

if tess_exit == True:
    code = getCaptchaPNG()
    while len(code) != 4:
        driver.find_element_by_id('btnCheck').click() #重新產生驗證碼
        time.sleep(2) # Wait for 2 sec
        getCaptchaPNG()
    print('驗證碼為: ' + code)
else:
    code = ""
    
sinput(driver, UserAct, UserPsd, code)    
