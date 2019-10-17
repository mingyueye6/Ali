# coding: utf-8
import datetime
import os

from Crypto.PublicKey import RSA

project_path = os.path.dirname(os.path.abspath(__file__)) # 项目所在路径
APPID = '2016092700608827'
ali_url = 'https://openapi.alipaydev.com/gateway.do' # 沙箱环境
private_key_path = os.path.join(project_path, 'private_key.txt')
public_key_path = os.path.join(project_path, 'public_key.txt')


class ali_login(object):
    __instance = None
    private_key = None
    public_key = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not ali_login.private_key:
            with open(private_key_path) as f:
                ali_login.private_key = RSA.importKey(f.read())
        self.private_key = ali_login.private_key
        if not ali_login.public_key:
            with open(public_key_path) as f:
                ali_login.public_key = RSA.importKey(f.read())
        self.public_key = ali_login.public_key

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

    # 第一步：客户端授权登录,获取code

    # 第二步：服务端通过code 获取 access_token
    def get_access_token(self, code):
        params = {
            'app_id': APPID,
            'method': 'alipay.system.oauth.token',
            'charset': 'utf-8',
            'sign_type': 'RSA2',
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'version': '1.0',
            'grant_type': 'authorization_code',
            'code': code
        }
        params_str = self.get_string(params)


    # 第三步：通过access_token调用接口,获取用户信息
    pass



if __name__ == '__mian__':
    ali = ali_login()
    ali.get_access_token('ceshi')

