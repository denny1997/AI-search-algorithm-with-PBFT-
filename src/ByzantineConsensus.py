def ByzantineConsensus(messageCollection,leader):
    count={}
    #print(messageCollection)
    for i,node in messageCollection:
        if i in count:
            count[i].append(node)
        else:
            count[i]=[node]
    maxnum=max(len(count[x]) for x in count)
    major=[]
    for i in count:
        if len(count[i])==maxnum and leader in count[i]:
            return i,count[i]
        elif len(count[i])==maxnum:
            major.append((i,count[i]))
    return major[0]