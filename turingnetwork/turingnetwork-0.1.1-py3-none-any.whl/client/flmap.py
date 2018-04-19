import torch


def fl_addmm(addmat, mat1, mat2, alpha=1, beta=1):
	return torch.addmm(addmat, mat1, mat2, alpha, beta)


pytorch2fl = {'aten::addmm': fl_addmm}
