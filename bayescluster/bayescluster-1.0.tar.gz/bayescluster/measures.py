
import numpy as np

## Function that gives all the nodes in a tree recursively
def get_allthenodes(tree,nodes):
    if tree==None:
        pass
    else:
        nodes.append(tree)
        get_allthenodes(tree.left,nodes)
        get_allthenodes(tree.right,nodes)
        
## Simple functions to keep track of points in the sets        
def contains(x,i,j):
    
    if i in x and j in x:
        return True
    else:
        return False
    
## Function that calculate the smallest subtree given the list of all nodes
def find_subtree(i,j,nodes):
    n=float('inf')
    for k in nodes :
        s=k.points
        if contains(s,i,j) and len(s)<n:
            res=k
            n=len(s)
    return res
        
def impurity(tree,yhat,y,n=100):
    impurity=0
    for i in range(n):
        a=np.arange(len(y))
        i=np.random.choice(a)
        clust=y[i]
        a=np.where(y==clust)[0]
        j=np.random.choice(a)
        nodes=[]
        get_allthenodes(tree,nodes)
        smallest=find_subtree(i,j,nodes)
        s=0
        for i in smallest.points:
            if[y[i]]==clust:
                s+=1
        ratio=s/len(smallest.points)
        impurity+=ratio
    impurity=impurity/n
    return impurity