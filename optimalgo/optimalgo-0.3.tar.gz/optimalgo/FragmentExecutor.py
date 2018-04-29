import time
class FragmentExecutor:
    def __init__(self,node_data):
        self.data = node_data
        self.instance_val(self.data)

    def instance_val(self,data):
        for node in data:
            work = False
            if node.out_data == []:
                continue
            out_val = []
            string = node.body
            try:
                t2_start = time.perf_counter()
                exec(string)
                t2_stop = time.perf_counter()
                work = True
            except:
                work = False

            if work == True:
                for var in node.out_data:
                    current_out = eval(var)
                    out_val.append(repr(current_out))
            node.value = out_val
            node.time = (t2_stop-t2_start)