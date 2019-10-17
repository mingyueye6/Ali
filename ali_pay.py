# coding: utf-8
import os

project_path = os.path.dirname(os.path.abspath(__file__)) # 项目所在路径
APPID = '2016092700608827'
private_key_path = os.path.join(project_path, 'private_key.txt')
public_key_path = os.path.join(project_path, 'public_key.txt')
ali_url = 'https://openapi.alipaydev.com/gateway.do'  # 沙箱环境


class ali_pay(object):
    pass


