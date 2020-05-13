import os
import json
import logging
import configparser  # ini

from win32com import client as wincom_client


# 取得Chrome版本號

def get_file_version(file_path):
    logging.debug('Get file version of [%s]', file_path)
    if not os.path.isfile(file_path):
        raise FileNotFoundError("找不到 {!r} .".format(file_path))

    wincom_obj = wincom_client.Dispatch('Scripting.FileSystemObject')
    version = wincom_obj.GetFileVersion(file_path)
    print('Chrome 版本為 ', version)
    return version.strip()


# 寫 json file
def write_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


# 讀 json file
def read_json(file_path):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except json.decoder.JSONDecodeError:  # JSON 為空
        logging.error('Empty mapping file')
        return {}


# 清除 json file 內容
def clear_json(file_path):
    with open(file_path, "w") as f:
        f.truncate(0)


class INI_object:
    def __init__(self):
        # function:  初始化INI檔案
        cntDir = os.path.split(os.path.realpath(__file__))[0]
        configPath = os.path.join(cntDir, "config.ini")
        # 創建對象
        self.conf = configparser.ConfigParser()
        # 讀取INI
        print("取得帳號, 密碼中...")
        self.conf.read(configPath, encoding='utf-8')

    def get(self, section, option):
        # function:  讀取INI檔案配置資訊.
        try:
            ret = self.conf.get(section, option)
            return ret
        except configparser.NoSectionError:
            print("不能獲取到%s選項 %s的值. 請確認 congin.ini 是否正確配置?" % (section, option))
            os.system("pause")
            exit(-1)
