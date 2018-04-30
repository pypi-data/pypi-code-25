from pkg import dist 
from pkg import k_means_int
from pkg import k_means_pp
from pkg import k_means
from pkg import scalable_k_means_pp

print dist.dist()
print k_means_int.k_means_int()
print k_means_pp.kmeanspp()
print k_means.k_means()
print scalable_k_means_pp.weights_c()
print scalable_k_means_pp.weighted_kmeans()
print scalable_k_means_pp.k_meansll()