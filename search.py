# search.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
#
# Created by Michael Abir (abir2@illinois.edu) on 08/28/2018

"""
This is the main entry point for MP1. You should only modify code
within this file -- the unrevised staff files will be used for all other
files and classes when code is run, so be careful to not modify anything else.
"""
# Search should return the path.
# The path should be a list of tuples in the form (row, col) that correspond
# to the positions of the path taken by your search algorithm.
# maze is a Maze object based on the maze from the file specified by input filename
# searchMethod is the search method specified by --method flag (bfs,dfs,astar,astar_multi,extra)

import queue
import datetime

def search(maze, searchMethod):
    return {
        "bfs": bfs,
        "dfs": dfs,
        "astar": astar,
        "astar_multi": astar_multi,
        "extra": extra,
    }.get(searchMethod)(maze)


def bfs(maze):
    """
    Runs BFS for part 1 of the assignment.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    # TODO: Write your code here
    #x,y=maze.getStart()
    path=[]
    for i in range(2):
        x, y = maze.getStart()[i]
        objx,objy=maze.getObjectives()[0]
        route={}
        que=queue.Queue()
        visited=[]
        result=[]
        curx=x
        cury=y
        while(curx!=objx or cury!=objy):
            pos=maze.getNeighbors(curx,cury)
            for item in pos:
                if item not in visited:
                    if item not in route:
                        que.put(item)
                        route[item]=(curx,cury)
            visited.append((curx,cury))
            curx,cury=que.get()
        while(curx!=x or cury!=y):
            result.append((curx,cury))
            curx,cury=route[(curx,cury)]
        result.append((x,y))
        result.reverse()
        path.append(result)
    return path


def dfs(maze):
    """
    Runs DFS for part 1 of the assignment.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    # TODO: Write your code here
    x,y=maze.getStart()
    objx,objy=maze.getObjectives()[0]
    route={}
    lst=[]
    visited=[]
    result=[]
    curx=x
    cury=y
    while(curx!=objx or cury!=objy):
        if (curx,cury) in visited:
            curx, cury = lst.pop()
            continue
        pos=maze.getNeighbors(curx,cury)
        # if len(pos)>=3:
        #     pos[1],pos[2]=pos[2],pos[1]
        for item in pos:
            if item not in visited:
                lst.append(item)
                route[item]=(curx,cury)
        visited.append((curx,cury))
        curx,cury=lst.pop()
    while(curx!=x or cury!=y):
        result.append((curx,cury))
        curx,cury=route[(curx,cury)]
    result.append((x,y))
    result.reverse()
    return result


def astar(maze):
    """
    Runs A star for part 1 of the assignment.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    # TODO: Write your code here
    x,y=maze.getStart()
    objx,objy=maze.getObjectives()[0]
    route={}
    priQue = []
    dis = {}
    result=[]
    curx=x
    cury=y
    dis[(x,y)]=0
    while True:
        pos = maze.getNeighbors(curx, cury)
        for item in pos:
            if (item not in dis )or (dis[(curx,cury)]+1 < dis[item]):
                dis[item]=dis[(curx,cury)]+1
                route[item]=(curx,cury)
                if item not in priQue:
                    priQue.append(item)
        if (objx,objy) in dis and dis[(objx,objy)]<=dis[(curx,cury)]:
            break
        priQue.sort(key=lambda x: dis[x]+abs(objx-x[0])+abs(objy-x[1]),reverse=True)
        curx, cury = priQue.pop()
    curx=objx
    cury=objy
    while (curx != x or cury != y):
        result.append((curx, cury))
        curx, cury = route[(curx, cury)]
    result.append((x, y))
    result.reverse()
    return result

def my_astar(maze,start,object):
    x,y=start
    objx,objy=object
    route={}
    priQue = []
    dis = {}
    result=[]
    curx=x
    cury=y
    dis[(x,y)]=0
    while True:
        pos = maze.getNeighbors(curx, cury)
        for item in pos:
            if (item not in dis )or (dis[(curx,cury)]+1 < dis[item]):
                dis[item]=dis[(curx,cury)]+1
                route[item]=(curx,cury)
                if item not in priQue:
                    priQue.append(item)
        if (objx,objy) in dis and dis[(objx,objy)]<=dis[(curx,cury)]:
            break
        priQue.sort(key=lambda x: dis[x]+abs(objx-x[0])+abs(objy-x[1]),reverse=True)
        curx, cury = priQue.pop()
    curx=objx
    cury=objy
    while (curx != x or cury != y):
        result.append((curx, cury))
        curx, cury = route[(curx, cury)]
    result.reverse()
    return result

def MinSpanTree(dis,route,p):
    # print(dis)
    # print(route)
    # print(p)
    path=[]
    points=[]
    for i in range(len(p)):
        if p[i] not in route or p[i]==route[len(route)-1]:
            points.append(i)
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
          path.append((points[i],points[j]))
    path.sort(key=lambda x:len(dis[x]))
    # for l in path:
    #     print(l,len(dis[l]))
    #print(path)
    kind=0
    belongs={}
    length=0
    for line in path:
        if len(belongs.keys())==len(points) and len(set(belongs.values()))==1:
            #print(length)
            break
        if line[0] not in belongs and line[1] not in belongs:
            belongs[line[0]]=kind
            belongs[line[1]]=kind
            kind+=1
            length+=len(dis[line])
        elif line[0] not in belongs:
            belongs[line[0]]=belongs[line[1]]
            length+=len(dis[line])
        elif line[1] not in belongs:
            belongs[line[1]]=belongs[line[0]]
            length+=len(dis[line])
        elif belongs[line[0]]==belongs[line[1]]:
            continue
        else:
            value=belongs[line[1]]
            for i in belongs.keys():
                if belongs[i]==value:
                    belongs[i]=belongs[line[0]]
            length+=len(dis[line])
    #print(length)
    return length


def astar_multi(maze,start,objects):
    """
    Runs A star for part 2 of the assignment in the case where there are
    multiple objectives.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    # TODO: Write your code here
    x, y = start
    objects = objects
    points=[(x,y)]+objects
    dis={}
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
            dis[(i,j)]=my_astar(maze,points[i],points[j])
            dis[(j,i)]=dis[(i,j)]
    # print(points)
    # for i in dis.keys():
    #     print(points[i[0]],points[i[1]],len(dis[i]))
    visited=[]
    #curx=x
    #cury=y
    priQue=[]
    #d={}
    #d[(x,y)]=0
    #route={}
    #route[(x,y)]=[(x,y)]
    #resdis=9999
    end=[]
    cur=([(x,y)],0)
    #print(dis)
    times=0
    max=[(x,y)]
    while True:
        # if len(cur[0])>maxlength:
        #     maxlength=len(cur[0])
        # elif len(cur[0])<maxlength/5:
        #     cur=priQue.pop()
        #     continue
        #print(len(set(cur[0])))
        # if (cur[0][len(cur[0])-1]) not in visited:
        #     visited.append((cur[0][len(cur[0])-1]))
        #     if len(set(cur[0]))==len(points):
        #         resdis=cur[1]
        #         end=cur[0]
        # if len(set(cur[0]))==len(points) and cur[1]<resdis:
        #     resdis = cur[1]
        #     end = cur[0]
        #     break
        #print(d)
        curx,cury=cur[0][len(cur[0])-1]
        # print(cur[0])
        t=[]
        for pts in points:
            #print(pts)
            #print(dis)
            #print((curx,cury),pts)
            #if pts==(curx,cury) or pts in cur[0]:
            if pts==(curx,cury) or pts in cur[0]:
                continue
            # if pts not in d or d[(curx,cury)]+len(dis[(points.index((curx,cury)),points.index(pts))])<d[pts]:
            #     d[pts]=d[(curx,cury)]+len(dis[(points.index((curx,cury)),points.index(pts))])
            #     route[pts]=route[(curx,cury)]+[(curx,cury)]
            #     #print(route)
            #     #print(pts)
            #     #print(route[pts])
            #     if pts not in priQue:
            #         priQue.append(pts)
            item=(cur[0]+[pts],cur[1]+len(dis[(points.index((curx,cury)),points.index(pts))]))
            # print(list(item)[0:int(len(max) / 4)])
            if len(item[0])<int(len(max)/4) or list(item[0])[0:int(len(max)/4)]!=max[0:int(len(max)/4)]:
                #print("garbage")
                continue
            #priQue.append(item)
            t.append(item)
        t.sort(key=lambda x:x[1]+MinSpanTree(dis,x[0],points))
        s=0
        # print(t)
        # print(priQue)
        while len(t)>0:
            k=t.pop()
            if s>=len(priQue):
                priQue.append(k)
                continue
            v=k[1]+MinSpanTree(dis,k[0],points)
            # print(s)
            # print(len(priQue))
            # print(priQue)
            # print(priQue[s][1])
            while priQue[s][1]+MinSpanTree(dis,priQue[s][0],points)>=v:
                s+=1
                if s >= len(priQue):
                    priQue.append(k)
                    break
            else:
                priQue.insert(s,k)
        #print(visited)
        #print(priQue)
        #priQue.sort(key=lambda x:x[1]+MinSpanTree(dis,x[0],points),reverse=True)
        #print(priQue)
        #print(len(priQue))
        #priQue.sort(key=lambda x: x[1] + MinSpanTree(dis, x[0], points), reverse=True)
        #print(dis)
        cur=priQue.pop()
        if len(cur[0])>len(max):
            max=cur[0]
        # elif max[0:int(len(max)/4)]!=cur[0][0:int(len(max)/4)]:
        #     print("garbage")
        #     cur=priQue.pop()
        #     continue
        # t=cur[1]+MinSpanTree(dis,cur[0],points)
        #if (len(visited)==len(points)) and cur[1]>resdis:
        if len(set(cur[0]))==len(points):
            #print(cur)
            end=cur[0]
            #end=[(7, 14), (4, 13), (1, 10), (4, 6), (1, 1), (6, 8), (6, 1), (9, 1), (11, 8), (11, 12), (11, 20), (9, 28), (10, 25), (9, 20), (7, 26), (6, 21), (4, 18), (2, 19), (3, 28)]
            break
        #curx,cury=next[0][len(next[0])-1]
        #print(resdis)
        # times+=1
        # if(times>200):
        #     return extra(maze)
    # for i in priQue:
    #     print(i[0],i[1]+MinSpanTree(dis,i[0],points))
    result=[]
    #print(visited)
    for i in range(len(end)-1):
        result+=my_astar(maze,end[i],end[i+1])
    result=[(x,y)]+result
    #print(len(priQue))
    return result

def extra(maze):
    """
    Runs extra credit suggestion.

    @param maze: The maze to execute the search on.

    @return path: a list of tuples containing the coordinates of each state in the computed path
    """
    # TODO: Write your code here
    x, y = maze.getStart()
    objects = maze.getObjectives()
    result = []
    FinishScan = []
    curx = x
    cury = y
    while len(FinishScan) != len(objects):
        length = []
        point = []
        for obj in objects:
            if obj in FinishScan:
                continue
            length.append(my_astar(maze, (curx, cury), obj))
            point.append(obj)
        min = len(length[0])
        minindex = 0
        for i in range(1, len(length)):
            if len(length[i]) < min:
                min = len(length[i])
                minindex = i
        result += length[minindex]
        FinishScan.append(point[minindex])
        curx, cury = point[minindex]
    result = [(x, y)] + result
    return result
