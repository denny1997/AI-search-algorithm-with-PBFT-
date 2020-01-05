import threading
import math
import private_chain
import time
from ByzantineConsensus import ByzantineConsensus
import crypto
import util

from search import astar_multi


class ByzantineNode(threading.Thread):
    def __init__(self, threadname,maze,startPos,messageQueue):
        threading.Thread.__init__(self, name=threadname)
        self.maze=maze
        self.startPos=startPos
        self.robotNum=len(maze.getStart())
        self.messageQueue=messageQueue
        self.privateChain = private_chain.PrivateChain()  # 创建私有链
        self.privateKey, self.publicKey = crypto.generateKeyPairs()
        util.savePrivateKey(self.name,self.privateKey)
        self.publicKeys={}

    def run(self):
        print('%s:Now timestamp is %s'%(self.name,time.time()))

        self.messageQueue.broadcast(self.name+"#"+self.publicKey)  # 广播公钥

        self.messageQueue.waitForMessage(self.name)

        for keysInfo in self.messageQueue.messageQueue[self.name]:
            node,key=keysInfo.split("#")
            self.publicKeys[node]=key

        # print(self.publicKeys)
        util.savePublicKeys(self.name,self.publicKeys)

        self.messageQueue.clearCacheMessage(self.name)

        # self.privateChain = private_chain.PrivateChain()  # 创建私有链
        #
        # self.privateKey,self.publicKey = crypto.generateKeyPairs()

        self.privateChain.curBlock.map = set(self.maze.getObjectives())  # 构建私有地图

        self.messageQueue.syncthreads(self.name)

        self.messageQueue.broadcast(self.name+"##"+str(self.privateChain.curBlock.map)+"##"+crypto.sign(self.privateKey,str(self.privateChain.curBlock.map)))  # 广播自己的地图和签名

        # while len(self.messageQueue.messageQueue[self.name])<self.robotNum:
        #     pass

        self.messageQueue.waitForMessage(self.name)

        validMsg=[]
        for msg in self.messageQueue.messageQueue[self.name]:
            node,plain,sign = msg.split("##")
            if crypto.verify(self.publicKeys[node],plain,sign):  # 验证签名
                validMsg.append(plain)

        self.privateChain.curBlock.map=eval(ByzantineConsensus(validMsg)) #完成拜占庭共识，对私有链中的地图进行修正，依照少数服从多数规则

        util.saveBlock(self.name,self.privateChain.curBlock,self.privateChain.curIndex)
        self.privateChain.generateNextBlock()  # 生成下一区块

        self.messageQueue.clearCacheMessage(self.name)

        objectNum = len(self.privateChain.curBlock.map)
        agentNum = self.robotNum
        averageNum = math.ceil(objectNum / agentNum)

        self.privateChain.curBlock.weightPos = {} #路径重心和任务集初始化
        self.privateChain.curBlock.tasks = {}
        self.privateChain.curBlock.eagernessGlob = {}
        for i in self.maze.getStart():
            self.privateChain.curBlock.weightPos[str(i)]=i
            self.privateChain.curBlock.tasks[str(i)]=[]
            eagerness = (averageNum - len(self.privateChain.curBlock.tasks[str(i)])) / averageNum

            if eagerness < 0:
                eagerness = 0

            self.privateChain.curBlock.eagernessGlob[str(i)] = (1.5 - eagerness) ** 5
            # self.privateChain.curBlock.eagernessGlob[str(i)] = 1
        #
        self.messageQueue.syncthreads(self.name) #线程同步

        for i in self.privateChain.curBlock.map:
            dis=float("inf")
            dis_name=None
            # flag = 0

            for p in self.maze.getStart():

                if abs(self.privateChain.curBlock.weightPos[str(p)][0] - i[0]) + \
                        abs(self.privateChain.curBlock.weightPos[str(p)][1] - i[1]) < \
                        dis / self.privateChain.curBlock.eagernessGlob[str(p)]:

                    dis=(abs(self.privateChain.curBlock.weightPos[str(p)][0] - i[0]) +
                        abs(self.privateChain.curBlock.weightPos[str(p)][1] - i[1])) * \
                        self.privateChain.curBlock.eagernessGlob[str(p)]
                    dis_name = str(p)

                elif abs(self.privateChain.curBlock.weightPos[str(p)][0] - i[0]) + \
                    abs(self.privateChain.curBlock.weightPos[str(p)][1] - i[1]) == \
                    dis / self.privateChain.curBlock.eagernessGlob[str(p)] and \
                    self.privateChain.curBlock.weightPos[str(p)][0] < self.privateChain.curBlock.weightPos[dis_name][0]:

                    dis_name = str(p)

                elif abs(self.privateChain.curBlock.weightPos[str(p)][0] - i[0]) + \
                    abs(self.privateChain.curBlock.weightPos[str(p)][1] - i[1]) == \
                    dis / self.privateChain.curBlock.eagernessGlob[str(p)] and \
                    self.privateChain.curBlock.weightPos[str(p)][0] == self.privateChain.curBlock.weightPos[dis_name][0] and \
                    self.privateChain.curBlock.weightPos[str(p)][1] < self.privateChain.curBlock.weightPos[dis_name][1]:

                    dis_name=str(p)

            self.messageQueue.broadcast(self.name+"##"+dis_name+"##"+crypto.sign(self.privateKey,dis_name))

            # while len(self.messageQueue.messageQueue[self.name]) < self.robotNum:
            #     pass
            self.messageQueue.waitForMessage(self.name)

            validMsg=[]
            for msg in self.messageQueue.messageQueue[self.name]:
                node, plain, sign = msg.split("##")
                if crypto.verify(self.publicKeys[node], plain, sign):  # 验证签名
                    validMsg.append(plain)

            n=ByzantineConsensus(validMsg)
            self.privateChain.curBlock.tasks[n].append(i)
            self.privateChain.curBlock.weightPos[n] = ((self.privateChain.curBlock.weightPos[n][0]+i[0])//2,(self.privateChain.curBlock.weightPos[n][1]+i[1])//2) #更新重心位置
            eagerness = (averageNum - len(self.privateChain.curBlock.tasks[n])) / averageNum
            if eagerness < 0:
                eagerness = 0
            #
            self.privateChain.curBlock.eagernessGlob[n] = (1.5 - eagerness) ** 5
            # self.privateChain.curBlock.eagernessGlob[n] = 1

            util.saveBlock(self.name, self.privateChain.curBlock, self.privateChain.curIndex)
            self.privateChain.generateNextBlock()  # 生成下一区块

            self.messageQueue.clearCacheMessage(self.name)

            self.messageQueue.syncthreads(self.name)

        print("from"+self.name)

        self.messageQueue.path[self.name]=astar_multi(self.maze, self.startPos,self.privateChain.curBlock.tasks[self.name]) #调用A*算法，返回路径
        self.privateChain.curBlock.path = self.messageQueue.path[self.name]

        util.saveBlock(self.name, self.privateChain.curBlock, self.privateChain.curIndex)
        self.privateChain.generateNextBlock()  #生成下一区块

