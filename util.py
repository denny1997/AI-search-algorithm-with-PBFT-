def syncthreads(system,selfObject):
    selfObject.curBlock.syncFlag=1
    selfObject.curBlock.syncReady=0
    while sum(x.curBlock.syncFlag for x in system.values())<len(system):
        pass
    selfObject.curBlock.syncReady=1
    while sum(x.curBlock.syncReady for x in system.values())<len(system):
        #print("qqqqq")
        pass
    selfObject.curBlock.syncFlag=0

def semaphoreWait(selfObject):
    selfObject.curBlock.semaphore=1
    while selfObject.curBlock.semaphore:
        pass

def semaphoreWaitToNotify(system):
    while sum(x.curBlock.semaphore for x in system.values())<len(system)-1:
        pass

def semaphoreNotify(system):
    for i in system.values():
        i.curBlock.semaphore=0