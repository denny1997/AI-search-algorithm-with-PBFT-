import threading
import math
import private_chain
import util
import time
from ByzantineSystem import ByzantineSystem

from search import astar_multi

class ByzantineNode(threading.Thread):
    def __init__(self, threadname,maze,startPos):
        threading.Thread.__init__(self, name=threadname)
        self.maze=maze
        self.startPos=startPos
        self.robotNum=len(maze.getStart())

    def run(self):
        print('%s:Now timestamp is %s'%(self.name,time.time()))
        self.privateChain = private_chain.PrivateChain() #创建私有链
        self.privateChain.curBlock.map = set(self.maze.getObjectives()) #构建私有地图
        #dic[self.name]=set(self.maze.getObjectives())
        ByzantineSystem[self.name]=self.privateChain #私有链加入拜占庭共识系统

        # while len(dic)<self.robotNum:
        #     pass
        while len(ByzantineSystem)<self.robotNum:  #等待所有节点上线
            pass
        count={}
        # for i in dic:
        #     if tuple(dic[i]) in count:
        #         count[tuple(dic[i])]+=1
        #     else:
        #         count[tuple(dic[i])]=1
        for i in ByzantineSystem:  #地图拜占庭共识开始
            if tuple(ByzantineSystem[i].curBlock.map) in count:
                count[tuple(ByzantineSystem[i].curBlock.map)]+=1
            else:
                count[tuple(ByzantineSystem[i].curBlock.map)]=1
        self.privateChain.curBlock.map=set(max(count,key=lambda x:count[x])) #完成拜占庭共识，对私有链中的地图进行修正，依照少数服从多数规则

        #weightPos[self.startPos] = self.startPos
        self.privateChain.curBlock.weightPos=self.startPos #路径重心初始化

        util.syncthreads(ByzantineSystem,self.privateChain) #线程同步

        # while len(weightPos)<self.robotNum:
        #     pass
        #waitCount[self.name]=0
        self.startPoints=self.maze.getStart()[:]
        print("from" + self.name, id(self.startPoints))
        self.startPoints.remove(self.startPos)
        self.newObjectPos=[]

        # modification starts
        #pendingTaskNum[self.name] = len(self.newObjectPos)
        self.privateChain.curBlock.pendingTaskNum = len(self.newObjectPos)
        objectNum = len(self.privateChain.curBlock.map)
        agentNum = len(ByzantineSystem)
        averageNum = math.ceil(objectNum/agentNum)


        # modification ends
        print("from" + self.name, self.startPoints,self.startPos)
        # for i in dic[self.name]:
        for i in self.privateChain.curBlock.map:
            eagerness = (averageNum - len(self.newObjectPos))/averageNum
            if eagerness<0:
                eagerness = 0
            #eagerWait[self.name]=0
            #eagernessGlob[self.startPos] = (1.5-eagerness)**5
            self.privateChain.curBlock.eagernessGlob = (1.5-eagerness)**5
            # eagerWait[self.name] = 1
            # while sum(eagerWait.values()) < agentNum:
            #     pass
            util.syncthreads(ByzantineSystem,self.privateChain) #线程同步
            #dis = abs(weightPos[self.startPos][0] - i[0]) + abs(weightPos[self.startPos][1] - i[1])
            dis=abs(self.privateChain.curBlock.weightPos[0]-i[0])+abs(self.privateChain.curBlock.weightPos[1]-i[1]) #计算当前节点到目标点的距离
            #print(eagernessGlob)
            #dis = dis * eagernessGlob[self.startPos]
            dis = dis * self.privateChain.curBlock.eagernessGlob
            # print(self.name, dis)
            for p in self.startPoints: #计算其他点到目标点是否有更短距离
                # if abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])<dis/eagernessGlob[p]:
                if abs(ByzantineSystem[str(p)].curBlock.weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].curBlock.weightPos[1] - i[1]) < dis / ByzantineSystem[str(p)].curBlock.eagernessGlob:
                    # waitCount[self.name]=1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain) #有更短距离，线程中断，等待该节点的信号量通知
                    break
                # elif abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])==dis/eagernessGlob[p] and weightPos[p][0]<weightPos[self.startPos][0]:
                elif abs(ByzantineSystem[str(p)].curBlock.weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].curBlock.weightPos[1] - i[1]) == dis / ByzantineSystem[str(p)].curBlock.eagernessGlob and ByzantineSystem[str(p)].curBlock.weightPos[0] < self.privateChain.curBlock.weightPos[0]:
                    # waitCount[self.name] = 1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain)
                    break
                # elif abs(weightPos[p][0]-i[0])+abs(weightPos[p][1]-i[1])==dis/eagernessGlob[p] and weightPos[p][0]==weightPos[self.startPos][0] and weightPos[p][1]<weightPos[self.startPos][1]:
                elif abs(ByzantineSystem[str(p)].curBlock.weightPos[0] - i[0]) + abs(ByzantineSystem[str(p)].curBlock.weightPos[1] - i[1]) == dis / ByzantineSystem[str(p)].curBlock.eagernessGlob and ByzantineSystem[str(p)].curBlock.weightPos[0] == self.privateChain.curBlock.weightPos[0] and ByzantineSystem[str(p)].curBlock.weightPos[1] < self.privateChain.curBlock.weightPos[1]:
                    # waitCount[self.name] = 1
                    # while waitCount[self.name]:
                    #     pass
                    util.semaphoreWait(self.privateChain)
                    break
            else: #更新属于自己的目标集合
                self.newObjectPos.append(i)
                #pendingTaskNum[self.name] = len(self.newObjectPos)
                self.privateChain.curBlock.pendingTaskNum = len(self.newObjectPos)
                # while sum(waitCount[x] for x in waitCount)<self.robotNum-1:
                #     pass
                util.semaphoreWaitToNotify(ByzantineSystem) #等待其他线程同步
                self.privateChain.curBlock.weightPos=((self.privateChain.curBlock.weightPos[0]+i[0])//2,(self.privateChain.curBlock.weightPos[1]+i[1])//2) #更新重心位置
                # for k in waitCount:
                #     waitCount[k]=0
                util.semaphoreNotify(ByzantineSystem) #信号量通知其他线程继续运行
        print("from"+self.name,self.newObjectPos)
        self.path = astar_multi(self.maze, self.startPos,self.newObjectPos) #调用A*算法，返回路径
        self.privateChain.curBlock.path=self.path
