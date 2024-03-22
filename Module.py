import time
import requests
import json
from datetime import datetime
class APIOperations:
    def __init__(self,url,pathparam=None,retype = None,files =None,param1=None,param2=None,json=None):
        self.url = url
        # self.port = port
        self.pathparam=pathparam
        self.retype = retype
        self.files = files
        self.param1 = param1
        self.param2 =param2
        self.json = json
        self.logs = GenerateLogs()
    def GetRequest(self):
        try:
            url1=self.url
            if self.pathparam is not None: url1= str(url1)+f'/{self.pathparam}'
            if self.param1 is not None: url1=url1.replace('#param1#',str(self.param1))
            if self.param2 is not None: url1=url1.replace('#param2#',str(self.param2))
            if any(rs in url1 for rs in ['GetMessageBox','GetTestStatus','GetAppState']):
                pass
            else:self.logs.Updatelogs("API call",url1)
            resp = requests.get(url1)
            if any(rs in url1 for rs in ['GetMessageBox','GetTestStatus','GetAppState']):
                pass
            else:self.logs.Updatelogs("API Response",resp.status_code)
            if resp:
                if self.retype == 'json':
                    return resp.json()
                elif self.retype == 'text':
                    return resp.text
                else: return resp.status_code
            return None
        except Exception as e:
            pass
            # self.logs.Updatelogs("Exception",str(e))
    def PutRequest(self):
        try:
            # url=self.url.replace("#port#",str(self.port))
            # print(url)
            if self.files is not None:
                resp = requests.put(self.url,files=self.files)
            elif self.json is not None:
                self.logs.Updatelogs("API call",f"{self.url},JSON:{self.json}")
                resp = requests.put(self.url,json=self.json)
            else:
                self.logs.Updatelogs("API call",self.url)
                resp = requests.put(self.url)
            self.logs.Updatelogs("API Response",resp.status_code)
            return int(resp.status_code)
        except Exception as e:
            # self.logs.Updatelogs("Exception",str(e))
            pass
    def PostRequest(self):
        try:
            if self.json is not None:
                self.logs.Updatelogs("API call",f"URL: {self.url},JSON:{self.json}")
                resp = requests.post(self.url,json=self.json)
            self.logs.Updatelogs("API Response",resp.status_code)
            return resp.status_code
        except Exception as e:
            # self.logs.Updatelogs("Exception",str(e))
            pass
class JsonOperations:
    def __init__(self,path):
        self.path =path
    def read_file(self):
        with open(self.path, "r") as rf:
            values = json.load(rf)
        return values
    def update_file(self,values):
        with open(self.path, "w") as outfile:
            json.dump(values, outfile)
    def defaultconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()
class GenerateLogs():
    def __init__(self):
        #Create log json file , if not Available.
        now = datetime.now()
        timestamp = now.strftime("%d%m%Y")
        self.Log = JsonOperations('Logs/'+timestamp+'.json')
        self.input = JsonOperations('json/input.json')
        self.inputData =self.input.read_file()
        try:
            self.LogData = self.Log.read_file()
        except Exception as e:
            self.inputData['LogFile'] = timestamp+'.json'
            self.input.update_file(self.inputData)
            self.Log.update_file({})
            self.LogData = self.Log.read_file()
    def Updatelogs(self,key,value):
        print(key,value)
        now = datetime.now()
        self.LogData = self.Log.read_file()
        timestamp =  str(now.strftime("%d%m%Y_%H%M%S"))+'_'+str((time.time_ns())%1000000000)
        if timestamp not in self.LogData:self.LogData[timestamp]=[]
        self.LogData[timestamp].append(f"{key}:{value}")
        self.Log.update_file(self.LogData)
        print(f"{timestamp} : {key} : {value}")
GenerateLogs()