#!/bin/env python
# -*- coding=utf-8 -*-
import random

from config.ticketConf import _get_yaml
from PIL import Image
from damatuCode.damatuWeb import DamatuApi
import requests
from init import gol


class go_login:
    def __init__(self, ticket_config = ""):
        self.captcha_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&%s' % random.random()
        self.ticket_config = ticket_config
        self.text = ""
        self.user = _get_yaml(ticket_config)["set"]["12306count"][0]["uesr"]
        self.passwd = _get_yaml(ticket_config)["set"]["12306count"][1]["pwd"]
        self.s = self.create_session()

    def create_session(self):
        s = requests.Session()
        return s


    def get_logincookies(self):
        global login_cookies,randCode
        init_url = "https://kyfw.12306.cn/otn/login/init"
        uamtk_data = {'appid': 'otn'}
        captcha_check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
        uamtk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        login_url = "https://kyfw.12306.cn/passport/web/login"
        login_userLogin = "https://kyfw.12306.cn/otn/login/userLogin"
        uamauthclient = "https://kyfw.12306.cn/otn/uamauthclient"
        self.s.get(init_url, verify=False)
        self.s.post(uamtk_url, data=uamtk_data, verify=False)
        requests.utils.add_dict_to_cookiejar(self.s.cookies, {"_jc_save_fromDate": '2018-01-27'})
        requests.utils.add_dict_to_cookiejar(self.s.cookies, {"_jc_save_toStation": '%u5170%u5DDE%u897F%2CLAJ'})
        requests.utils.add_dict_to_cookiejar(self.s.cookies, {"_jc_save_toDate": '2018-01-22'})
        requests.utils.add_dict_to_cookiejar(self.s.cookies, {"_jc_save_wfdc_flag": 'dc'})
        requests.utils.add_dict_to_cookiejar(self.s.cookies, {"_jc_save_fromStation": '%u4E0A%u6D77%u8679%u6865%2CAOH'})
        randCode = self.get_randcode()
        randdata = {"answer": randCode,
                   "login_site": "E",
                   "rand": "sjrand"}
        login_data = {"username": self.user,
                      "password": self.passwd,
                      "appid": "otn"}
        rand_result = self.s.post(captcha_check_url, data=randdata, verify=False).json()
        print(rand_result)  #{'result_message': '验证码校验失败', 'result_code': '5'}
        while rand_result['result_code'] is not '4' :
            randCode = self.get_randcode()
            randdata = {"answer": randCode,
                        "login_site": "E",
                        "rand": "sjrand"}
            rand_result = self.s.post(captcha_check_url, data=randdata, verify=False).json()
            print(rand_result)

        login_result = self.s.post(login_url, allow_redirects=False, data=login_data, verify=False)
        login_code = login_result.status_code
        print(login_code)
        #解决登录接口302重定向问题
        while login_code == 302 :
            login_result = self.s.post(login_url, allow_redirects=False, data=login_data, verify=False)
            login_code = login_result.status_code
            if login_code == 200 :
                print(login_result.json())
        login_userLogin_data = {'_json_att' : ''}
        self.s.post(login_userLogin, data=login_userLogin_data, verify=False)
        uamtk_result = self.s.post(uamtk_url, allow_redirects=False, data=uamtk_data, verify=False)
        while uamtk_result.status_code == 302 :
            uamtk_result = self.s.post(uamtk_url, allow_redirects=False, data=uamtk_data, verify=False)
        uamtk_result = uamtk_result.json()
        print(uamtk_result) #{'result_message': '验证通过', 'result_code': 0, 'apptk': None, 'newapptk': '4gUWVNUUUItHlpM5Mpl3Hb252KZpPxKSdhgDSNy5HCYr1Hb3tyb2b0'}
        #如果账户未登录，下面一行会抛出异常，即键newapptk不存在
        uamauthclient_data = {'tk': uamtk_result['newapptk']}
        uamauthclient_result = self.s.post(uamauthclient, data=uamauthclient_data, verify=False).json()
        print(uamauthclient_result)
        login_cookies = self.s.cookies.get_dict()
        return login_cookies


    def get_randcode(self):
        self.stoidinput("下载验证码...")
        img_path = './tkcode'
        r = self.s.get(self.captcha_url, verify=False)
        result = r.content
        # print(result)
        try:
            open(img_path, 'wb').write(result)
            if _get_yaml(self.ticket_config)["is_aotu_code"]:
                randCode = DamatuApi(_get_yaml(self.ticket_config)["damatu"]["uesr"],
                                     _get_yaml(self.ticket_config)["damatu"]["pwd"], img_path).main()

            else:
                img = Image.open('./tkcode')
                img.show()
                randCode = self.codexy()
        except OSError as e:
            print(e)
            pass
        print(randCode)
        return randCode


    def stoidinput(self,text):
        """
        正常信息输出
        :param text:
        :return:
        """
        print("\033[34m[*]\033[0m %s " % text)


    def errorinput(self,text):
        """
        错误信息输出
        :param text:
        :return:
        """
        print("\033[32m[!]\033[0m %s " % text)
        return False


    def codexy(self):
        """
        获取验证码
        :return: str
        """
        global randCode
        Ofset = input("[*] 请输入验证码: ")
        select = Ofset.split(',')
        #global randCode
        post = []
        offsetsX = 0  # 选择的答案的left值,通过浏览器点击8个小图的中点得到的,这样基本没问题
        offsetsY = 0  # 选择的答案的top值
        for ofset in select:
            if ofset == '1':
                offsetsY = 41
                offsetsX = 39
            elif ofset == '2':
                offsetsY = 44
                offsetsX = 110
            elif ofset == '3':
                offsetsY = 49
                offsetsX = 184
            elif ofset == '4':
                offsetsY = 45
                offsetsX = 253
            elif ofset == '5':
                offsetsY = 116
                offsetsX = 39
            elif ofset == '6':
                offsetsY = 113
                offsetsX = 110
            elif ofset == '7':
                offsetsY = 120
                offsetsX = 184
            elif ofset == '8':
                offsetsY = 121
                offsetsX = 257
            else:
                pass
            post.append(offsetsX)
            post.append(offsetsY)
        randCode = str(post).replace(']', '').replace('[', '').replace("'", '').replace(' ', '')
        return randCode


    def login(self):
        self.get_logincookies()
        gol._init()
        gol.set_value('s',self.s)

    #
    # def getUserinfo(self):
    #     """
    #     登录成功后,显示用户名
    #     :return:
    #     """
    #     url = 'https://kyfw.12306.cn/otn/modifyUser/initQueryUserInfo'
    #     data = dict(_json_att=None)
    #     #result = myurllib2.myrequests().post(url, data).decode('utf-8')
    #     result = self.s.post(url,data=data,verify=False).content
    #     userinfo = result
    #     name = r'<input name="userDTO.loginUserDTO.user_name" style="display:none;" type="text" value="(\S+)" />'
    #     try:
    #         self.stoidinput("欢迎 %s 登录" % re.search(name, result).group(1))
    #     except AttributeError:
    #         pass




    def logout(self):
        url = 'https://kyfw.12306.cn/otn/login/loginOut'
        result = self.s.get(url, verify=False).json()
        if result:
            self.stoidinput("已退出")
        else:
            self.errorinput("退出失败")


# if __name__ == "__main__":
#     go_login.login()
    # logout()