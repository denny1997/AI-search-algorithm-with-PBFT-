import json
class Block:
    def __init__(self):
        self.lastBlockHash=None
        self.map=None
        self.path=None
        self.weightPos=None
        self.tasks=None
        self.eagernessGlob=None
        # self.syncFlag=0
        # self.syncReady=0
        # self.semaphore=0

    def __str__(self):
        return json.dumps({'lastBlockHash':self.lastBlockHash,'map':self.map,'path':self.path,'weightPos':self.weightPos,'tasks':self.tasks,'eagernessGlob':self.eagernessGlob})

# a=Block()
# a.lastBlockHash={1:[2,3]}
# print(a)