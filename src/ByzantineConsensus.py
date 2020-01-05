def ByzantineConsensus(messageCollection):
    count={}
    for i in messageCollection:
        if i in count:
            count[i] += 1
        else:
            count[i] = 1
    return max(count, key=lambda x: count[x])