## Define a new class called note which has the data points d_k and the number of the cluster


import numpy as np
from scipy.special import factorial,multigammaln
from decimal import Decimal

class Node:


    
    def __init__(self,p,alpha,i):
        
        self.single=True
        self.points=set()
        self.points.add(p)
        self.d=alpha
        self.number=i
        self.left=None
        self.right=None
        self.ph=0
            
    def add(self,x):
        self.points.add(x)
        
    def add_all(self,x):
        self.points=x
        
    def remove(self,x):
        self.points.remove(x)
        
    def combine(self,y,alpha):
        p=self.points.union(y.points)
        z=Node(1,self.d,self.number)
        z.left=self
        z.right=y
        z.remove(1)
        z.points=p
        z.d= alpha*factorial(len(p)-1)+self.d*y.d
        z.single=False
        return z 
        
def prob_hypo(X,kappa0,v0,mu0,eta0):
    from decimal import Decimal
    nf,df= X.shape
    n=Decimal(nf)
    d=Decimal(df)
    a= (1/(Decimal(np.pi))**(n*d/2))
    b=Decimal(multigammaln((v0+nf)/2,df)/multigammaln(v0/2,df))
    S=np.zeros((df,df))
    for i in range(nf):
        o=X[i]-X.mean(axis=0)
        S+=np.outer(o,o)
    etan=(eta0) + S + (kappa0*nf/(kappa0+nf))*np.outer((X.mean(axis=0)-mu0),(X.mean(axis=0)-mu0))
    c=Decimal(np.linalg.det(eta0)**(v0/2))/(Decimal(np.linalg.det(etan))**((Decimal(v0)+n)/2))
    d=Decimal(kappa0/(kappa0+nf))**(d/2)
    return float(a*b*c*d)

## Function that initiates clusters
def init(X,alpha,kappa0,v0,mu0,eta0):
    x=[]
    for i in range(len(X)):
        node=Node(i,alpha,i)
        node.ph=prob_hypo(X[[i]],kappa0,v0,mu0,eta0)
        x.append(node)
        
    return x

## Making the loop faster-- Only loop to fill the upper triangular part of the numpy matrix
def calculate_r(nodes,alpha,X,kappa0,v0,mu0,eta0):
    from scipy.special import factorial
    n=len(nodes)
    rik=np.zeros((n,n))
    pit=np.zeros((n,n))
    for i in range(n):
        for j in range(i+1,n):
            clust_k=nodes[i].combine(nodes[j],alpha)
            nk=len(clust_k.points)
            dk=clust_k.d
            pi=alpha*factorial(nk-1)/dk
            all_points=list(clust_k.points)
            ph=prob_hypo(X[all_points][:],kappa0,v0,mu0,eta0) 
            pt=ph*pi+ (1-pi)*nodes[i].ph*nodes[j].ph
            pit[i,j]=pt
            rik[i,j]=(pi*ph)/pt
            
    
## Function for updating clusters, by creating a new node (combination of i and j) and deleting nodes i,j
def update_clust(rk,pit,nodes,alpha):
    i,j=np.unravel_index(np.argmax(rk),rk.shape)
    if len(nodes[i].points)>len(nodes[j].points):
        new_node=nodes[i].combine(nodes[j],alpha)
    else:
        new_node=nodes[j].combine(nodes[i],alpha)
    new_node.single=False
    new_node.ph=pit[i,j]
    nodes[i]=new_node 
    del nodes[j]
    return nodes

def clust(X,alpha,kappa0,v0,mu0,eta0,k=3):
    nodes=init(X,alpha,kappa0,v0,mu0,eta0)
   
    for i in range(len(nodes)-k):
        rk,pit=calculate_r(nodes,alpha,X,kappa0, v0,mu0, eta0)
        nodes=update_clust(rk,pit,nodes,alpha)
    y=np.zeros(len(X))
    for i in range(k):
        ind=list(nodes[i].points)
        y[ind]=i
    for i in range(k-1):
        rk,pit=calculate_r(nodes,alpha,X,kappa0,v0,mu0,eta0)
        nodes=update_clust(rk,pit,nodes,alpha)
        
    return y,nodes[0]
            