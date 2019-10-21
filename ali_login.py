# coding: utf-8
# 未测试，不知道能不能使用
import base64
import datetime
import json
import os

import requests
import rsa
from urllib.parse import urlencode

project_path = os.path.dirname(os.path.abspath(__file__)) # 项目所在路径
APPID = '2016092700608827'
private_key_path = os.path.join(project_path, 'private_key.pem')
public_key_path = os.path.join(project_path, 'public_key.pem')
ali_url = 'https://openapi.alipaydev.com/gateway.do?{}' # 沙箱环境


class Ali_Login(object):
    __instance = None
    private_key = None
    public_key = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not Ali_Login.private_key:
            with open(private_key_path, 'rb') as f:
                Ali_Login.private_key = rsa.PrivateKey.load_pkcs1(f.read())
        self.private_key = Ali_Login.private_key
        if not Ali_Login.public_key:
            with open(public_key_path, 'rb') as f:
                Ali_Login.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(f.read())
        self.public_key = Ali_Login.public_key

    # 获取格式化参数
    def get_string(self, params):
        slist = sorted(params)
        buff = []
        for k in slist:
            if not params[k]:
                continue
            v = str(params[k])
            buff.append("{0}={1}".format(k, v))
        return "&".join(buff)

    # 签名
    def get_sign(self, params):
        params_str = self.get_string(params)
        sign = rsa.sign(params_str.encode('utf-8'), Ali_Login.private_key, 'SHA-256')
        sign = base64.b64encode(sign).decode('utf-8')
        return sign

    # 第一步：客户端授权登录,获取code

    # 第二步：服务端通过code 获取 access_token
    def get_access_token(self, code):
        params = {
            'app_id': APPID,
            'method': '	alipay.open.auth.token.app',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'biz_content': {
                'grant_type': 'authorization_code',
                'code': code
            }
        }
        params['sign'] = self.get_sign(params)
        data_str = urlencode(params)
        url = ali_url.format(data_str)
        res = requests.get(url)
        content = res.json()
        data = content['alipay_open_auth_token_app_response']
        sign = content['sign']
        if data['code'] == '10000' and data['msg'] == 'Success':
            app_auth_token = data['app_auth_token']
            return app_auth_token
        return ''


    # 第三步：通过access_token调用接口,获取用户信息
    def get_infos(self, code):
        # token = self.get_access_token(code)
        token = '20130319e9b8d53d09034da8998caefa756c4006'
        params = {
            'app_id': APPID,
            'method': 'alipay.user.info.share',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'auth_token': token
        }
        params['sign'] = self.get_sign(params)
        data_str = urlencode(params)
        url = ali_url.format(data_str)
        res = requests.get(url)
        content = res.json()
        print(content)
        data = content['alipay_user_info_share_response']
        sign = content['sign']



if __name__ == '__main__':
    ali = Ali_Login()
    ali.get_infos('ceshi')

