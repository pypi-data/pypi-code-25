def make_gene(single_param_obj):
    gene = []
    for i in range(5):
        gene.append(single_param_obj.w[i].copy())
        gene.append(single_param_obj.b[i].copy())
    return gene