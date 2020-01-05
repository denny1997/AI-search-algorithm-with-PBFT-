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
    path=[]
    points=[]
    for i in range(len(p)):
        if p[i] not in route or p[i]==route[len(route)-1]:
            points.append(i)
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
          path.append((points[i],points[j]))
    path.sort(key=lambda x:len(dis[x]))
    kind=0
    belongs={}
    length=0
    for line in path:
        if len(belongs.keys())==len(points) and len(set(belongs.values()))==1:
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
    return length


def astar_multi(maze,start,objects):
    x, y = start
    objects = objects
    points=[(x,y)]+objects
    dis={}
    for i in range(len(points)-1):
        for j in range(i+1,len(points)):
            dis[(i,j)]=my_astar(maze,points[i],points[j])
            dis[(j,i)]=dis[(i,j)]
    priQue=[]
    cur=([(x,y)],0)
    max=[(x,y)]
    while True:
        curx,cury=cur[0][len(cur[0])-1]
        t=[]
        for pts in points:
            if pts==(curx,cury) or pts in cur[0]:
                continue
            item=(cur[0]+[pts],cur[1]+len(dis[(points.index((curx,cury)),points.index(pts))]))
            if len(item[0])<int(len(max)/4) or list(item[0])[0:int(len(max)/4)]!=max[0:int(len(max)/4)]:
                continue
            t.append(item)
        t.sort(key=lambda x:x[1]+MinSpanTree(dis,x[0],points))
        s=0
        while len(t)>0:
            k=t.pop()
            if s>=len(priQue):
                priQue.append(k)
                continue
            v=k[1]+MinSpanTree(dis,k[0],points)
            while priQue[s][1]+MinSpanTree(dis,priQue[s][0],points)>=v:
                s+=1
                if s >= len(priQue):
                    priQue.append(k)
                    break
            else:
                priQue.insert(s,k)
        cur=priQue.pop()
        if len(cur[0])>len(max):
            max=cur[0]
        if len(set(cur[0]))==len(points):
            end=cur[0]
            break
    result=[]
    for i in range(len(end)-1):
        result+=my_astar(maze,end[i],end[i+1])
    result=[(x,y)]+result
    return result

