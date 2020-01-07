import threading
import math
import private_chain
import time
from ByzantineConsensus import ByzantineConsensus
from maze import Maze
import crypto
import util

from search import astar_multi


class ByzantineNode(threading.Thread):
    def __init__(self, threadname,filename,startPos,messageQueue):
        threading.Thread.__init__(self, name=threadname)
        self.maze=Maze(filename+self.name)
        self.startPos=startPos
        self.robotNum=len(self.maze.getStart())
        self.messageQueue=messageQueue
        self.privateChain = private_chain.PrivateChain()  # 创建私有链
        self.privateKey, self.publicKey = crypto.generateKeyPairs()
        util.savePrivateKey(self.name,self.privateKey)
        self.publicKeys={}
        self.privateChain.curBlock.leader=str(tuple(self.maze.getStart()[0]))
        self.leaderWaitList=self.maze.getStart()[1:]

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
                validMsg.append((plain,node))
            else:
                self.privateChain.curBlock.message+="Sign verification for node "+node+" failed! "

        consensusRes,group=ByzantineConsensus(validMsg,self.privateChain.curBlock.leader) #完成拜占庭共识，对私有链中的地图进行修正，依照少数服从多数规则
        self.privateChain.curBlock.map=eval(consensusRes)

        for plain,node in validMsg:
            if node not in group:
                self.privateChain.curBlock.message+="Node "+node+"'s local map "+plain+" has been corrected to "+consensusRes+"! "
                if node in self.leaderWaitList:  # 失去成为领导节点的机会
                    self.leaderWaitList.remove(node)

        if self.privateChain.curBlock.leader not in group:  # 重新选举领导节点
            if len(self.leaderWaitList)>0:
                self.privateChain.curBlock.leader=str(tuple(self.leaderWaitList[0]))
                self.leaderWaitList=self.leaderWaitList[1:]
                self.privateChain.curBlock.message+="Old leader corrupted, new leader has been elected! "
            else:
                self.privateChain.curBlock.leader=None
                self.privateChain.curBlock.message+="All nodes corrupted, leader abolished in the system! "

        util.saveBlock(self.name,self.privateChain.curBlock,self.privateChain.curIndex)
        self.privateChain.generateNextBlock()  # 生成下一区块

        self.messageQueue.clearCacheMessage(self.name)

        objectNum = len(self.privateChain.curBlock.map)
        agentNum = self.robotNum
        averageNum = math.ceil(objectNum / agentNum)

        self.privateChain.curBlock.weightPos = {} #路径重心和任务集初始化
        self.privateChain.curBlock.tasks = {}
        self.privateChain.curBlock.eagernessGlob = {}
        self.privateChain.curBlock.pathLengthGlob = {}

        # parameters
        # (eagernessBase - eagerness) ** eagernessExp

        # best record: 76 ↓
        eagernessBase = 1.5
        eagernessExp = 2
        pathLengthExp = 0.2

        # eagernessBase = 1.5
        # eagernessExp = 0
        # pathLengthExp = 0




        for i in self.maze.getStart():
            self.privateChain.curBlock.weightPos[str(i)]=i
            self.privateChain.curBlock.tasks[str(i)]=[]
            eagerness = (averageNum - len(self.privateChain.curBlock.tasks[str(i)])) / averageNum

            if eagerness < 0:
                eagerness = 0

            self.privateChain.curBlock.eagernessGlob[str(i)] = (eagernessBase - eagerness) ** eagernessExp
            # self.privateChain.curBlock.eagernessGlob[str(i)] = 1
            self.privateChain.curBlock.pathLengthGlob[str(i)] = 1

        self.messageQueue.syncthreads(self.name) #线程同步

        orderedMap = []
        distanceDic = {}
        for i in self.privateChain.curBlock.map:
            minDistance = float('inf')
            for p in self.maze.getStart():
                distance = len(astar_multi(self.maze, p, [i]))
                if distance < minDistance:
                    minDistance = distance
            if minDistance not in distanceDic:
                distanceDic[minDistance] = [i]
            else:
                distanceDic[minDistance].append(i)

        allDistance = distanceDic.keys()
        allDistance = sorted(allDistance)

        for dis in allDistance:
            goalList = distanceDic[dis]
            orderedMap.extend(goalList)

        print(allDistance)
        print(distanceDic)
        print(orderedMap)

        for i in orderedMap:
        # for i in self.privateChain.curBlock.map:
            # print(i)
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
                    validMsg.append((plain,node))
                else:
                    self.privateChain.curBlock.message += "Sign verification for node " + node + " failed! "

            n,group=ByzantineConsensus(validMsg,self.privateChain.curBlock.leader)
            self.privateChain.curBlock.tasks[n].append(i)
            # 更新重心位置
            self.privateChain.curBlock.weightPos[n] = ((self.privateChain.curBlock.weightPos[n][0]+i[0])//2,(self.privateChain.curBlock.weightPos[n][1]+i[1])//2) #更新重心位置

            eagerness = (averageNum - len(self.privateChain.curBlock.tasks[n])) / averageNum
            if eagerness < 0:
                eagerness = 0
            #
            self.privateChain.curBlock.eagernessGlob[n] = (eagernessBase - eagerness) ** eagernessExp
            # self.privateChain.curBlock.eagernessGlob[n] = 1

            if len(self.privateChain.curBlock.tasks[n]) >= 1:
                self.privateChain.curBlock.pathLengthGlob[n] = len(astar_multi(self.maze, eval(n),self.privateChain.curBlock.tasks[n]))
                # print("not empty", self.name)
            else:
                self.privateChain.curBlock.pathLengthGlob[n] = 1
                # print("empty", self.name)

            # print(type(self.privateChain.curBlock.eagernessGlob[n]), type(self.privateChain.curBlock.pathLengthGlob[n]))
            #print(self.privateChain.curBlock.pathLengthGlob[n])

            self.privateChain.curBlock.eagernessGlob[n] = self.privateChain.curBlock.eagernessGlob[n] * self.privateChain.curBlock.pathLengthGlob[n]**pathLengthExp

            print(self.name, self.privateChain.curBlock.tasks[self.name], self.privateChain.curBlock.pathLengthGlob[self.name],self.privateChain.curBlock.eagernessGlob[self.name])

            for plain, node in validMsg:
                if node not in group:
                    self.privateChain.curBlock.message += "Node " + node + "'s task distribution for " + plain + " has been corrected to " + n + "! "
                    if node in self.leaderWaitList:  # 失去成为领导节点的机会
                        self.leaderWaitList.remove(node)

            if self.privateChain.curBlock.leader not in group:  # 重新选举领导节点
                print(group)
                if len(self.leaderWaitList) > 0:
                    self.privateChain.curBlock.leader = str(tuple(self.leaderWaitList[0]))
                    self.leaderWaitList = self.leaderWaitList[1:]
                    self.privateChain.curBlock.message += "Old leader corrupted, new leader has been elected! "
                else:
                    self.privateChain.curBlock.leader = None
                    self.privateChain.curBlock.message += "All nodes corrupted, leader abolished in the system! "

            util.saveBlock(self.name, self.privateChain.curBlock, self.privateChain.curIndex)
            self.privateChain.generateNextBlock()  # 生成下一区块

            self.messageQueue.clearCacheMessage(self.name)

            self.messageQueue.syncthreads(self.name)

        print("from"+self.name)

        self.messageQueue.path[self.name]=astar_multi(self.maze, self.startPos,self.privateChain.curBlock.tasks[self.name]) #调用A*算法，返回路径
        self.privateChain.curBlock.path = self.messageQueue.path[self.name]

        util.saveBlock(self.name, self.privateChain.curBlock, self.privateChain.curIndex)
        self.privateChain.generateNextBlock()  #生成下一区块

