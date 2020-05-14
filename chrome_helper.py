import os
import logging
import zipfile

import requests

import file_util

DEBUG_MSG = "[DEBUG]"
CURRENT_PATH = os.getcwd()  # 當前資料夾路徑
CHROME_DRIVER_BASE_URL = "https://chromedriver.storage.googleapis.com"
CHROME_DRIVER_FOLDER = CURRENT_PATH + r"\temp\chrome"
CHROME_DRIVER_MAPPING_FILE = r"{}\mapping.json".format(CHROME_DRIVER_FOLDER)
CHROME_DRIVER_EXE = r"{}\chromedriver.exe".format(CHROME_DRIVER_FOLDER)
CHROME_DRIVER_ZIP = r"{}\chromedriver_win32.zip".format(CHROME_DRIVER_FOLDER)


# 取得當前 Chrome 版本

def get_chrome_driver_major_version():
    chrome_browser_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    chrome_ver = file_util.get_file_version(chrome_browser_path)
    chrome_major_ver = chrome_ver.split(".")[0]
    return chrome_major_ver


# 取得 driver 最後發行版本

def get_latest_driver_version(browser_ver):
    latest_api = "{}/LATEST_RELEASE_{}".format(
        CHROME_DRIVER_BASE_URL, browser_ver)
    resp = requests.get(latest_api)
    lastest_driver_version = resp.text.strip()
    return lastest_driver_version


# 下載/更新 driver

def download_driver(driver_ver, dest_folder):
    download_api = "{}/{}/chromedriver_win32.zip".format(
        CHROME_DRIVER_BASE_URL, driver_ver)
    dest_path = os.path.join(dest_folder, os.path.basename(download_api))
    resp = requests.get(download_api, stream=True, timeout=300)  # 下載檔案

    if resp.status_code == 200:  # 同 == requests.codes.ok
        with open(dest_path, "wb") as f:
            f.write(resp.content)
        print("chrome driver 下載完畢")
    else:
        raise Exception("chrome driver 下載失敗")


def unzip_driver_to_target_path(src_file, dest_path):
    with zipfile.ZipFile(src_file, 'r') as zip_ref:
        zip_ref.extractall(dest_path)
    logging.info("Unzip [{}] -> [{}]".format(src_file, dest_path))


# 讀取 map 檔案

def read_driver_mapping_file():
    driver_mapping_dict = {}
    if os.path.isfile(CHROME_DRIVER_MAPPING_FILE):  # isfile
        driver_mapping_dict = file_util.read_json(CHROME_DRIVER_MAPPING_FILE)
    else:
        logging.error("[ERROR] On read_driver_mapping_file, mapping file at " + CHROME_DRIVER_MAPPING_FILE + "is not "
                                                                                                             "exist.")
        exit(-1)
    return driver_mapping_dict


# 檢查是否有可用的 driver 版本

def check_browser_driver_available():
    chrome_major_ver = get_chrome_driver_major_version()
    mapping_dict = read_driver_mapping_file()
    driver_ver = get_latest_driver_version(chrome_major_ver)

    if chrome_major_ver not in mapping_dict:  # 沒有版本號
        download_driver(driver_ver, CHROME_DRIVER_FOLDER)
        unzip_driver_to_target_path(CHROME_DRIVER_ZIP, CHROME_DRIVER_FOLDER)
        mapping_dict = {
            chrome_major_ver: {
                "driver_path": CHROME_DRIVER_EXE,
                "driver_version": driver_ver
            }
        }
        mapping_dict.update(mapping_dict)
        file_util.write_json(CHROME_DRIVER_MAPPING_FILE, mapping_dict)
    else:
        print('取得chrome driver.')
    '''
    # 避免檔案不見 mapping 卻還在
    if (os.path.isfile(CHROME_DRIVER_EXE) or os.path.exists(CHROME_DRIVER_EXE)) is False:
        file_util.clear_json(CHROME_DRIVER_MAPPING_FILE)
        print("ERROR", CHROME_DRIVER_EXE, os.path.isfile(CHROME_DRIVER_EXE), os.path.exists(CHROME_DRIVER_EXE))
        # check_browser_driver_available()
    '''


if __name__ == "__main__":
    check_browser_driver_available()
