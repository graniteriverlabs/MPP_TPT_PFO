from Module import APIOperations,JsonOperations
class CheckStatus():
    def __init__(self):
        self.input = JsonOperations('json/input.json')
        self.inputData =self.input.read_file()
        self.APIForceStop = APIOperations(url=f"http://{self.inputData['PCIP']}:2004/api/TestConfiguration/StopTestExecution")
    #To force stop the live run.
    def ForceStop(self):
        self.APIForceStop.GetRequest()
FS = CheckStatus()
FS.ForceStop()