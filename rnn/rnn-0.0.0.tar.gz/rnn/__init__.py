import argparse
import tensorflow as tf

LSTMCell = tf.nn.rnn_cell.LSTMCell


class RNN():

    def __init__(self, cell, projections=None, projection=None, return_sequences=True):
        projection = projection if projections is None else tf.layers.Dense(projections)
        self._cell = cell
        self._projection = projection
        self._return_sequences = return_sequences
        self._state = None

    def __call__(self, x, dtype=tf.float32):
        outputs, self._state = tf.nn.dynamic_rnn(self.cell, x, dtype=dtype)
        outputs = self.projection(outputs)
        if not self._return_sequences:
            outputs = outputs[:, -1, :]
        return outputs

    @property
    def cell(self):
        return self._cell

    @property
    def projection(self):
        return self._projection

    @property
    def state(self):
        return self._state


class LSTM(RNN):

    def __init__(self, units, projections=None, projection=None, *arguments, **keywords):
        cell = LSTMCell(units, *arguments, **keywords)
        super(LSTM, self).__init__(cell, projections=projections, projection=projection)


class Generator():

    def __init__(self, rnn, projection=None, prediction=None):
        if projection is None:
            projection = (lambda x: x) if rnn.projection is None else rnn.projection
        if prediction is None:
            prediction = lambda x: tf.contrib.seq2seq.hardmax(x)
        self._cell = rnn.cell if hasattr(rnn, 'cell') else rnn
        self._projection = projection
        self._prediction = prediction
        self._state = None

    def init_state(self, batch_size, dtype=tf.float32):
        self._state = self.cell.zero_state(batch_size, dtype)

    def reset(self):
        self._state = None

    def __call__(self, x, length):
        if self._state is None:
            self.init_state(x.shape[0])
        outputs = [x]
        for _ in range(length):
            x, self._state = self.cell(x, self._state)
            x = self.projection(x)
            x = self.prediction(x)
            outputs.append(x)
        return outputs

    @property
    def cell(self):
        return self._cell

    @property
    def projection(self):
        return self._projection

    @property
    def prediction(self):
        return self._prediction

    @property
    def state(self):
        return self._state


def cli(**keywords):
    parser = argparse.ArgumentParser()
    for name, value in keywords.items():
        type_ = None if value is None else type(value)
        parser.add_argument('--' + name, default=value, type=type_)
    return parser.parse_args()
