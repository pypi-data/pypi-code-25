from .model import Model


class Concatenated(Model):
    def __init__(self, layer):
        Model.__init__(self)
        self._layers.append(layer)
        self.on_data_hooks.append(on_data)

    @property
    def nO(self):
        return self._layers[0].nO + self._layers[0].nI

    @property
    def nI(self):
        return self._layers[0].nI

    def __call__(self, X):
        Y = self._layers[0](X)
        if isinstance(X, list) or isinstance(X, tuple):
            return [self.ops.xp.hstack([Y[i], X[i]]) for i in range(len(X))]
        else:
            return self.ops.xp.hstack([Y, X])

    def begin_update(self, X, drop=0.):
        y, bp_y = self._layers[0].begin_update(X, drop=drop)
        if isinstance(X, list) or isinstance(X, tuple):
            output = [self.ops.xp.hstack((y[i], X[i])) for i in range(len(X))]
            nr_y = y[0].shape[1]
        else:
            output = self.ops.xp.hstack((y, X))
            nr_y = y.shape[1]
        def concatenated_bwd(d_output, sgd=None):
            if isinstance(d_output, list) or isinstance(d_output, tuple):
                dY = []
                for i in range(len(d_output)):
                    dY.append(self.ops.xp.ascontiguousarray(d_output[i][:, :nr_y]))
                dX = bp_y(dY, sgd=sgd)
                for i in range(len(d_output)):
                    dX[i] += d_output[i][:, nr_y:]
            else:
                dY = self.op.xp.ascontiguousarray(d_output[:, :nr_y])
                dX = bp_y(dY, sgd=sgd)
                dX += d_output[:, nr_y:]
            return dX
        return output, concatenated_bwd


def on_data(self, X, y=None):
    for layer in self._layers:
        for hook in layer.on_data_hooks:
            hook(layer, X, y)
        if hasattr(layer, 'W'):
            layer.W.fill(0)
