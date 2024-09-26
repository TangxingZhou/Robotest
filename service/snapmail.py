import os
import re
import requests
from datetime import datetime
from fixture.internal.instance import env


email_prefix = 'mocloud'


def get_mails(email):
    res = requests.get(f"https://www.snapmail.cc/emailList/{email}?count=10")
    assert res.status_code == 200
    for m in res.json():
        if m['html']['subject'] == '[MO-Cloud] 注册验证':
            return re.search(r'href="(.*)">点击激活</a>', m['html']).groups()[0]


def activate(url):
    res = requests.get(url)
    assert res.status_code == 200


def signup(firstname,
           lastname,
           email=None,
           password=os.getenv('INSTANCE_PASSWORD', 'Admin123'),
           company="矩阵起源",
           mobile_number='1',
           *purpose):
    # 个人学习和开发
    # 替换已有的数据库
    # 在新的应用平台上探索数据库
    # 其他：
    if not email:
        email = f"{email_prefix}{datetime.now().strftime('%Y%m%d%H%M%S')}@snapmail.cc"
    res = requests.post(f"{env.get_config('auth_url')}/trial/signup",
                        json={
                            "firstname": firstname,
                            "lastname": lastname,
                            "company": company,
                            "email": email,
                            "mobile_number": mobile_number,
                            "password": password,
                            "purpose": list(purpose),
                            "agreed_to_policy": False
                        })
    assert res.status_code == 200 and res.json()['code'] == 'OK'
    return email, password
