class PrivateChain:
    def __init__(self):
        self.map=None
        self.path=None
        self.weightPos=None
        self.pendingTaskNum=None
        self.eagernessGlob=None
        self.syncFlag=0
        self.syncReady=0
        self.semaphore=0

    def sysout(self):
        print("------------------")
        print("map",self.map)
        print("path",self.path)
        print("weight",self.weightPos)
        print("pend",self.pendingTaskNum)
        print("eager",self.eagernessGlob)
        print("sync",self.syncFlag)
        print("sema",self.semaphore)
        print("------------------")