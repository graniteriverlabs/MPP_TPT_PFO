import glob
import os
import shutil
import time
import requests
import json
from datetime import datetime
from Module import APIOperations,JsonOperations,GenerateLogs
class APIControl():
    def __init__(self):
    #Get JSON data
        self.input = JsonOperations('json/input.json')
        self.inputData =self.input.read_file()
        self.Qi = JsonOperations('json/QIconfig.json')
        self.QiData =self.Qi.read_file()
        self.AppPro = JsonOperations('C:\\GRL\\GRL-C3-MP-TPT\\AppData\\AppProperty.json')
        self.AppProData = self.AppPro.read_file()
        self.ExcrPkt = JsonOperations('json/PutTPTPacketInformation.json')
        self.ExcrPktData = self.ExcrPkt.read_file()
        self.logs = GenerateLogs()
        self.Power={'2.5':19,'5':32,'7.5':'4B','10':64,'12.5':'7D','15':96}
        self.NewDir = None
        #Global Vars
        self.ConsoleIP = self.inputData["PCIP"]
        #Connection
        self.EnableExcelReport()
        self.ConnectTester()
        if self.inputData['ConnectionStatus']==0:
            while True:
                print("--------------------------------------------")
                print("1.Run 0,0 Test")
                print("2.Run 2,2 Test")
                print("3.Exit")
                print("--------------------------------------------")
                option = input("Enter the choice :")
                if option =='1':self.RunTC('00')
                elif option =='2':self.RunTC('22')
                elif option =='3':break
                else:print('Invalid Choice.! Try Again.')
    def RunTC(self,pos):
        now = datetime.now()
        timestamp =  str(now.strftime("%d%m%Y_%H%M%S"))+'_'+str((time.time_ns())%1000000000)
        self.NewDir = os.path.join('Reports',timestamp)
        os.makedirs(self.NewDir)
        for Pow in self.Power:
            self.SetPowerECAP(self.Power[Pow])
            #PutPhases
            APIGPhase = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/CustomAPIConfiguration_MPPTPT/GetDefaultTPTPhaseSettings",retype='json')
            APIGPhaseData = APIGPhase.GetRequest()
            APIPPhase = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/CustomAPIConfiguration_MPPTPT/PutTPTPhaseSettings",json=APIGPhaseData)
            APIPPhase.PutRequest()
            #Put Packets
            APIPPktData = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/CustomAPIConfiguration_MPPTPT/PutTPTPacketInformation",json=self.ExcrPktData)
            APIPPktData.PutRequest()
            #coil
            APIPCoil =APIOperations(url=f"http://{self.ConsoleIP}:2004/api/CustomAPIConfiguration_MPPTPT/PutSelectedQiSpecMode/MPP")
            APIPCoil.PutRequest()
            #Buttonstatus
            APIPBtn =APIOperations(url=f"http://{self.ConsoleIP}:2004/api/TestConfiguration/PutExecutionButtonStatus",json={"fodStartTestCaseInProgress":False,"fodStartCaptureInProgress":True,"optimumCoilInProgress":False,"loadRampInProgress":False,"testStatusInProgress":False,"readCapsInProgress":False})
            APIPBtn.PutRequest()
            #StartTest
            APIPutStartTC = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/CustomAPIConfiguration_MPPTPT/PutStartExerciser")
            APIPutStartTC.PutRequest()
            #Qi
            APIQI = APIOperations(url=f"http://{self.inputData['PCIP']}:2004/api/TestConfiguration/PutQIConfiguration",json=self.QiData)
            APIQI.PutRequest()
            #Monitor test for 1.5 minis & stop.
            print(f"Test Execution in Progress :{Pow} W")
            if Pow in ['2.5','5','7.5']:
                end = time.time() + 60 * 1
            elif pow in ['10','12.5']:
                end = time.time() + 60 * 1.5
            else: end = time.time() + 60 * 2
            while time.time() < end:
                pass
            # Force stop test
            APIForceStop = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/TestConfiguration/StopTestExecution")
            APIForceStop.GetRequest()
            print("Test Execution Ended")
            print("Reports Saving...")
            time.sleep(10)
            self.CreateReportFolder(Pow,pos)
    def ConnectTester(self):
        #Connection
        self.inputData["ConnectionStatus"]= 1
        print(f"Existing Connection Server/PC IP :{self.inputData['PCIP']}, TesterIP :{self.inputData['TesterIP']}")
        ExCon = input("Proceed with existing connection setup?(Y/N) :")
        ExCon=ExCon.upper()
        if ExCon=='N':
            #Provide New Connection Parameters.
            self.inputData["PCIP"] = input("Provide SW running PC/Server IP:")
            self.inputData["TesterIP"] = input("Provide Tester IP Addess:")
            self.input.update_file(self.inputData)
            self.inputData =self.input.read_file()
        self.ConsoleIP = self.inputData["PCIP"]
        self.logs.Updatelogs("Connection",f"Connection proceeding with : Server/PC IP :{self.inputData['PCIP']}, TesterIP :{self.inputData['TesterIP']}")
        # print(f"Connection proceeding with : Server/PC IP :{self.inputData['PCIP']}, TesterIP :{self.inputData['TesterIP']}")
        TesterCon = APIOperations(url=f"http://{self.ConsoleIP}:2004/api/ConnectionSetup",pathparam=self.inputData['TesterIP'],retype='json')
        try:
            testerinfo = TesterCon.GetRequest()
            if testerinfo is not None:
                if testerinfo['testerStatus'] == 'Connected':
                    self.logs.Updatelogs("Connection","Tester Connected..")
                    self.inputData["ConnectionStatus"] = 0
                else:self.logs.Updatelogs("Connection","Tester Not Available.!")
            else:self.logs.Updatelogs("Connection","None response for API")
        except Exception as e:
           self.logs.Updatelogs("Exception",str(e))
        self.input.update_file(self.inputData)
        self.inputData = self.input.read_file()
    def EnableExcelReport(self):
        self.AppProData['Enable_Calibration_Assertions']['DefaultValue']=True
        self.AppProData['Enable_Calibration_Assertions']['PropertyValue']=True
        self.AppPro.update_file(self.AppProData)
    def SetPowerECAP(self,PowVal):
        self.ExcrPktData['data'][1]['negotiationPhase'][0]['selectedPacketsPayLoadList'][3]['selectedValue']=PowVal
        self.ExcrPktData['data'][1]['negotiationPhase'][0]['selectedPacketsPayLoadList'][5]['selectedValue']=PowVal
        self.ExcrPkt.update_file(self.ExcrPktData)
        self.ExcrPktData  = self.ExcrPkt.read_file()
    def CreateReportFolder(self,pow,pos):
        #GetRecent files CSV
        list_of_files = glob.glob('C:\\GRL\\GRL-C3-MP-TPT\\Report\\OfflineReport\\PacketLog_Exerciser\\*')
        latest_CSV_file = max(list_of_files, key=os.path.getctime)
        DestCSV = os.path.join(self.NewDir,f"{pow}_{pos}.csv")
        DestTrace=os.path.join(self.NewDir,f"{pow}_{pos}.grltrace")
        shutil.move(latest_CSV_file,DestCSV)
        #Get Trace
        Tracepath_list = []
        for root, dirs, files in os.walk('C:\GRL\GRL-C3-MP-TPT\SignalFiles'):
            for file in files:
                if file == 'QiSignalCapture.grltrace':
                    #Tracepath_list.append(os.path.join(root,file))
                    RecentTrace = os.path.join(root,file)
                    shutil.move(RecentTrace,DestTrace)
                    break
TPR = APIControl()