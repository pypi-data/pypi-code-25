import torch

from .python_tracer import PythonTracer
from .flmap import pytorch2fl



class FlashLight:
    """ The interface class """

    # TODO - pytorch/onnx version check
    def __init__(self, net):
        self.net = net

    def show_dynamic(self, x):
        """ Slow exploration but captures everything, works only in PyTorch """
        with PythonTracer() as pyt:
            trace, out = torch.jit.get_trace_graph(self.net, x)
            print(trace.graph())
            exit()
            # out = torch._C.GraphExecutor(trace.graph(), optimize=True)(x)
            for node in trace.graph().nodes():
                print(node)

    def show_static(self, x):
        """ Fast exploration, wont make dynamic graph, default option for
        graphing from ONNNX
        """
        pass

    def show_trace(self, x):
        trace, out = torch.jit.get_trace_graph(self.net, x)
        print(trace)

    @staticmethod
    def print(*args):
        if 0:
            print(*args)
