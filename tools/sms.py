import datetime
import  hashlib
import  base64
import json

import  requests

class YunTongXin():
    base_url='https://app.cloopen.com:8883'


    def __init__(self,accountSid,accountToken,appid,tenplateId):
        self.accountSid=accountSid
        self.accountToken=accountToken
        self.appId=appid
        self.templateId=tenplateId


    def get_request_url(self, sig):

        self.url=self.base_url+'/2013-12-26/Accounts/%s/SMS/TemplateSMS?sig=%s'%(self.accountSid,sig)
        return  self.url

    def get_timestamp(self):
        #生成时间戳
        now = datetime.datetime.now()
        now_str = now.strftime("%Y%m%d%H%M%S")
        return  now_str

    def get_sig(self,timestamp):





        s= self.accountSid+self.accountToken+timestamp

        m=hashlib.md5()

        m.update(s.encode())
        return  m.hexdigest().upper()

    def get_reqyest_header(self,timestamp):
        s= self.accountSid+":"+timestamp
        b_s = base64.b64encode(s.encode()).decode()
        return  {
            'Accept':'application/json',
            'Content-Type':'application/json;charset=utf-8;',
            'Authorization':b_s

        }

    def request_body(self,phone,code):
        #构建请求体
        data={
            'to':phone,
            'appId':self.appId,
            'templateId':self.templateId,
            'datas':[code,'3']



        }
        return  data

    def do_request(self,url,header,body):
        res=  requests.post(url,headers=header,data=json.dumps(body))
        return  res.text


    def run(self,phone, code):
        timestamp=self.get_timestamp()
        sig = self.get_sig(timestamp)
        url= self.get_request_url(sig)
        header = self.get_reqyest_header(timestamp)
        body = self.request_body(phone,code)

        res = self.do_request(url, header, body)
        return res
if __name__ == '__main__':
    aid="8aaf0708730554fa017309ce9a4f0174"
    atoken="83686eda1ee645b190056deda6a88913"
    appid = '8aaf0708730554fa017309ce9b65017a'
    tid = "1"
    x = YunTongXin(aid, atoken, appid, tid)
    res = x.run('15833245909', '881227')
    print(res)