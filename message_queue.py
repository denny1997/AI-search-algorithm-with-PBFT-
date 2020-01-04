class MessageQueue:
    def __init__(self, startPos):
        self.messageQueue={}
        self.syncMessageQueue={}
        self.path={}
        for start in startPos:
            self.messageQueue[str(start)]=[]
            self.syncMessageQueue[str(start)]=[]

    def broadcast(self, msg):
        for node in self.messageQueue:
            self.messageQueue[node].append(msg)

    def clearAllCacheMessage(self):
        for node in self.messageQueue:
            self.messageQueue[node]=[]

    def clearCacheMessage(self, node):
        self.messageQueue[node]=[]

    def syncthreads(self, node):
        for i in self.syncMessageQueue:
            self.syncMessageQueue[i].append("sync")
        while len(self.syncMessageQueue[node])<len(self.syncMessageQueue):
            pass
        self.syncMessageQueue[node]=[]