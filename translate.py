import requests
import json
from pprint import pprint
import logging
import configparser

config = configparser.ConfigParser()
config.read("config.ini")


def trans(query: str):
        
    url = "https://aip.baidubce.com/rpc/2.0/mt/texttrans/v1?access_token=" + get_access_token()
    
    payload = json.dumps({
        "from": "en",
        "to": "zh",
        "q": query
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    logging.debug(f'query {query}, res {response.text}')
    
    return response.json()


def trans_esay(query: str):
    res = trans(query=query)
    if res is None or 'result' not in res:
        print("翻译失败:", res)
        return None
    return res['result']['trans_result'][0]['dst']

def get_access_token():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    API_KEY = config.get("baidu", "API_KEY")
    SECRET_KEY = config.get("baidu", "SECRET_KEY")
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    logging.debug(f'get_access_token params {params}')
    sign_res = requests.post(url, params=params)
    logging.debug(f'get_access_token sign_res {sign_res.text}')
    token = str(sign_res.json().get("access_token"))
    logging.debug(f'get_access_token token {token}')
    return token

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    ans = trans_esay(input("输入需要翻译的文本"))
    print(ans)