class SaveWeightsBias(object):
    def __init__(self, w_list, b_list):
        self.w = w_list
        self.b = b_list


def create_param(n_task, w_list, b_list):
    param = []
    for i in range(n_task):
        param.append(SaveWeightsBias(w_list, b_list))
    return param
