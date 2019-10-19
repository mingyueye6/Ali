# coding: utf-8
import datetime
import base64
import os
import requests
import rsa
from urllib.parse import urlencode

project_path = os.path.dirname(os.path.abspath(__file__)) # 项目所在路径
APPID = "2016092700608827"
private_key_path = os.path.join(project_path, "private_key.pem")
public_key_path = os.path.join(project_path, "public_key.pem")
ali_url = "https://openapi.alipaydev.com/gateway.do?{}"  # 沙箱环境
notify_url = "http://http://118.24.155.213:8000/payment"  # 支付宝异步回调地址，用于处理订单结果
return_url = "http://118.24.155.213:8000"  # 支付宝同步回调地址，用于网页支付完成跳转页面


class Ali_Pay(object):
    __instance = None
    private_key = None
    public_key = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        if not Ali_Pay.private_key:
            with open(private_key_path, "rb") as f:
                Ali_Pay.private_key = rsa.PrivateKey.load_pkcs1(f.read())
        self.private_key = Ali_Pay.private_key
        if not Ali_Pay.public_key:
            with open(public_key_path, "rb") as f:
                Ali_Pay.public_key = rsa.PublicKey.load_pkcs1_openssl_pem(f.read())
        self.public_key = Ali_Pay.public_key

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
        sign = rsa.sign(params_str.encode("utf-8"), Ali_Pay.private_key, "SHA-256")
        sign = base64.b64encode(sign).decode("utf-8")
        return sign

    # 异步回调验签
    def check_sign(self, data, sign):
        if "sign_type" in data:
            data.pop("sign_type")
        if "sign" in data:
            data.pop("sign")
        params_str = self.get_string(data)
        sign = base64.b64decode(sign)
        params_str = params_str.encode("utf-8")
        try:
            rsa.verify(params_str, sign, Ali_Pay.public_key)
        except:
            return False
        else:
            return True

    # 统一收单下单并支付页面接口
    def get_trade_page(self, out_trade_no, total_amount, subject):
        params = {
            "app_id": APPID,
            "method": "alipay.trade.page.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": notify_url,
            "biz_content": {
                "out_trade_no": out_trade_no,
                "product_code": "FAST_INSTANT_TRADE_PAY",
                "total_amount": total_amount,
                "subject": subject
            },
            "return_url": return_url
        }
        params["sign"] = self.get_sign(params)
        data_str = urlencode(params)
        url = ali_url.format(data_str)
        return url

    # app支付接口
    def get_app_pay(self, out_trade_no, total_amount, subject):
        params = {
            "app_id": APPID,
            "method": "alipay.trade.app.pay",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "notify_url": notify_url,
            "biz_content": {
                "out_trade_no": out_trade_no,  # 商家订单号
                "total_amount": total_amount,  # 订单金额
                "subject": subject  # 订单描述
            }
        }
        params["sign"] = self.get_sign(params)
        data_str = urlencode(params)
        return data_str

    # 统一收单交易退款接口
    def refund_trade_page(self, refund_amount, trade_no=None, out_trade_no=None, refund_reason=None):
        params = {
            "app_id": APPID,
            "method": "alipay.trade.refund",
            "charset": "utf-8",
            "sign_type": "RSA2",
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "1.0",
            "biz_content": {
                "refund_amount": refund_amount,  # 退款金额
            }
        }
        if trade_no:
            params["biz_content"]["trade_no"] = trade_no  # 支付宝订单号
        else:
            params["biz_content"]["out_trade_no"] = out_trade_no  # 商家订单号
        if refund_reason:
            params["biz_content"]["refund_reason"] = refund_reason  # 退款原因
        # params["sign"] = self.get_sign(params)
        # params_str = urlencode(params)
        # url = ali_url.format(params_str)
        # res = requests.get(url)
        # res = res.json()
        res = {"alipay_trade_refund_response": {"code": "10000", "msg": "Success", "buyer_logon_id": "bav***@sandbox.com", "buyer_user_id": "2088102177778750", "fund_change": "Y", "gmt_refund_pay": "2019-10-19 15:46:16", "out_trade_no": "12345678909", "refund_fee": "10.11", "send_back_fee": "0.00", "trade_no": "2019101922001478751000146234"}, "sign": "k+z9Xo3D7SB8bpGr3dXQufu/4GQwbL6n5CyoZ8vMZwa+OYdhS3HXPdSRvrZgh9sX3btmSOqJMWiOUwV9UA+WfvFJc8Sndy+yoZQCPVorFv5B7F/5a+yhXBcFOkl5PdzT/a2EAbw36zXid0WnB5qLgcEImZk3VnRRp0T4QsAlX1ZmOSVqjDnbLjHgxfurnulkPVM99MZrG10YF7ZBuMUKNQQHbiTIE90QOILX3kMDjNKYBgyxNR+nJyZLo5BvUH5OavfFDw9XEWk9+PEQI3YHJM7E+cAZyBIm/OUQtdCtDp9TNV7e9jThk28kxtTwlOo9ie6rTcWKO5s43+5NBluCsg=="}
        sign = res.get("sign", "")
        data = res.get("alipay_trade_refund_response", "")



if __name__ == "__main__":
    ali = Ali_Pay()
    # 测试下单
    # url = ali.get_trade_page("12345678909", 10.11, "测试金额")
    # ali.get_app_pay("12345678908", 10.11, "测试金额")
    ali.refund_trade_page(10.11, out_trade_no="12345678909", refund_reason="测试金额")
    # 支付宝回调验签
    # body = {"gmt_create": "2019-10-19 10:40:05", "charset": "utf-8", "gmt_payment": "2019-10-19 10:40:14", "notify_time": "2019-10-19 10:43:24", "subject": "测试金额", "sign": "F37fDRp1FH214t4kraFZ4LaqwT6PG1T2vXbxh16rtjtVYe4IZifviywbf0zK6C4lNjmHQAaoVhvzLW0GxO19m3bCA5hWQHBtq6NH4Ad33W2iS1qdlNDiVjuVgA+fbMo2waEoN+hBIzSe9en4usCY3JTpiYDaP+NbxYvweIjrJRB1spap9I4bQ3YOgm1QLnZhwQyhaEbS2zn2/QIhkjF8rumlCNSDwvLqmaZVrELxygZWC9dtFAQcGBcbuiv1orC7G6gmrQjAR2zv+8nAFkGhjeAg4Ljq9HbV9Kc9l4uzgMGnbCjctW3DznXPbrJ2SD89LUqHXMw2GoE/MV0AB6w3+g==", "buyer_id": "2088102177778750", "invoice_amount": "10.11", "version": "1.0", "notify_id": "2019101900222104014078751000623751", "fund_bill_list": "[{"amount":"10.11","fundChannel":"ALIPAYACCOUNT"}]", "notify_type": "trade_status_sync", "out_trade_no": "12345678905", "total_amount": "10.11", "trade_status": "TRADE_SUCCESS", "trade_no": "2019101922001478751000146232", "auth_app_id": "2016092700608827", "receipt_amount": "10.11", "point_amount": "0.00", "app_id": "2016092700608827", "buyer_pay_amount": "10.11", "sign_type": "RSA2", "seller_id": "2088102177517300"}
    # sign = body.pop("sign", "")
    # if ali.check_sign(body, sign):
    #     print("验签通过，处理订单")
    # else:
    #     print("验签失败")

