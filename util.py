def syncthreads(system,selfObject):
    selfObject.syncFlag=1
    selfObject.syncReady=0
    while sum(x.syncFlag for x in system.values())<len(system):
        pass
    selfObject.syncReady=1
    while sum(x.syncReady for x in system.values())<len(system):
        #print("qqqqq")
        pass
    selfObject.syncFlag=0

def semaphoreWait(selfObject):
    selfObject.semaphore=1
    while selfObject.semaphore:
        pass

def semaphoreWaitToNotify(system):
    while sum(x.semaphore for x in system.values())<len(system)-1:
        pass

def semaphoreNotify(system):
    for i in system.values():
        i.semaphore=0