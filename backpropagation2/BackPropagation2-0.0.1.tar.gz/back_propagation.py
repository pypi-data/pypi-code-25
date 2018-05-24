import random
import typing
import math

__version__ = '0.0.1'
__author__ = 'WingC'
__email__ = '1018957763@qq.com'
__description__ = 'Python Package for Back Propagation Implement'
__github__ = 'https://github.com/Wingsgo/Back_Propagation'
__name__ = 'BackPropagation2'


#
#   参数解释：
#   "pd_" ：偏导的前缀
#   "d_" ：导数的前缀
#   "w_ho" ：隐含层到输出层的权重系数索引
#   "w_ih" ：输入层到隐含层的权重系数的索引

class NeuralNetwork:
    LEARNING_RATE = 0.5

    def __init__(self,
                 num_inputs,  # 输入数据
                 num_hidden,  # 隐层神经元个数
                 num_outputs,  # 输出层神经元个数
                 hidden_layer_weights=None, hidden_layer_bias=None,  # 输入层--->隐层的weight与bias
                 output_layer_weights=None, output_layer_bias=None):  # 隐层--->输出层的weight与bias

        self.num_inputs = num_inputs

        self.hidden_layer = NeuronLayer(num_hidden, hidden_layer_bias)
        self.output_layer = NeuronLayer(num_outputs, output_layer_bias)

        self.init_weights_from_inputs_to_hidden_layer_neurons(hidden_layer_weights)
        self.init_weights_from_hidden_layer_neurons_to_output_layer_neurons(output_layer_weights)

    # 随机初始化输入层--->隐层的weight
    def init_weights_from_inputs_to_hidden_layer_neurons(self, hidden_layer_weights):
        weight_num = 0
        for h in range(len(self.hidden_layer.neurons)):
            for j in range(self.num_inputs):
                if not hidden_layer_weights:
                    self.hidden_layer.neurons[h].weights.append(random.random())
                else:
                    self.hidden_layer.neurons[h].weights.append(hidden_layer_weights[weight_num])
                weight_num += 1

    # 随机初始化隐层--->输出层的weight
    def init_weights_from_hidden_layer_neurons_to_output_layer_neurons(self, output_layer_weights):
        weight_num = 0
        for o in range(len(self.output_layer.neurons)):
            for h in range(len(self.hidden_layer.neurons)):
                if not output_layer_weights:
                    self.output_layer.neurons[o].weights.append(random.random())
                else:
                    self.output_layer.neurons[o].weights.append(output_layer_weights[weight_num])
                weight_num += 1

    # 给定输入得到前向传播的输出
    def feed_forward(self, inputs) -> typing.List:
        hidden_layer_outputs = self.hidden_layer.feed_forward(inputs)
        return self.output_layer.feed_forward(hidden_layer_outputs)

    def train(self, training_inputs, training_outputs):
        self.feed_forward(training_inputs)

        # 1. 计算隐层--->隐层的权值更新 [∂E/∂netO1, ∂E/∂netO2]
        pd_e_neto = [0] * len(self.output_layer.neurons)
        for o in range(len(self.output_layer.neurons)):
            pd_e_neto[o] = self.output_layer.neurons[
                o].calculate_pd_lsm_sigmoid(training_outputs[o])

        # 2. 隐含层神经元的值 pd_e_neth = [∂E/∂neth1, ∂E/∂neth2]
        pd_e_neth = [0] * len(self.hidden_layer.neurons)
        for h in range(len(self.hidden_layer.neurons)):
            # ∂E/∂netO * ∂netO/∂outh = ∂E/∂outh
            d_e_outh = sum(
                [pd_e_neto[o] * self.output_layer.neurons[o].weights[h] for o in range(len(self.output_layer.neurons))])

            # ∂E/∂neth = ∂E/∂outh * ∂outh/∂neth
            pd_e_neth[h] = d_e_outh * self.hidden_layer.neurons[h].calculate_pd_sigmoid()

        # 3. 更新输出层权重系数
        for o in range(len(self.output_layer.neurons)):
            for w_ho in range(len(self.output_layer.neurons[o].weights)):
                # ∂Eⱼ/∂wᵢⱼ = ∂E/∂zⱼ * ∂zⱼ/∂wᵢⱼ
                pd_error_wrt_weight = pd_e_neto[o] * self.output_layer.neurons[
                    o].calculate_pd_feed_forward(w_ho)

                # Δw = α * ∂Eⱼ/∂wᵢ
                self.output_layer.neurons[o].weights[w_ho] -= self.LEARNING_RATE * pd_error_wrt_weight

        # 4. 更新隐含层的权重系数
        for h in range(len(self.hidden_layer.neurons)):
            for w_ih in range(len(self.hidden_layer.neurons[h].weights)):
                # ∂Eⱼ/∂wᵢ = ∂E/∂zⱼ * ∂zⱼ/∂wᵢ
                pd_error_wrt_weight = pd_e_neth[h] * self.hidden_layer.neurons[
                    h].calculate_pd_feed_forward(w_ih)

                # Δw = α * ∂Eⱼ/∂wᵢ
                self.hidden_layer.neurons[h].weights[w_ih] -= self.LEARNING_RATE * pd_error_wrt_weight

    def calculate_total_error(self, training_sets):
        total_error = 0
        for t in range(len(training_sets)):
            training_inputs, training_outputs = training_sets[t]
            self.feed_forward(training_inputs)
            for o in range(len(training_outputs)):
                total_error += self.output_layer.neurons[o].calculate_error(training_outputs[o])
        return total_error

    def inspect(self):
        print('------')
        print('* Inputs: {}'.format(self.num_inputs))
        print('------')
        print('Hidden Layer')
        self.hidden_layer.inspect()
        print('------')
        print('* Output Layer')
        self.output_layer.inspect()
        print('------')


class NeuronLayer:
    # 初始化Layer的神经元个数与偏置
    def __init__(self, num_neurons, bias):

        # 同一层的神经元共享一个截距项b
        self.bias = bias if bias else random.random()
        self.neurons = [Neuron(self.bias) for j in range(num_neurons)]

    # 前向传播计算该Layer的output
    def feed_forward(self, inputs) -> typing.List:
        return [neuron.calculate_output(inputs) for neuron in self.neurons]

    def get_outputs(self):
        return [neuron.output for neuron in self.neurons]

    # 查看该Layer的权重
    def inspect(self):
        print('Neurons:', len(self.neurons))
        for n in range(len(self.neurons)):
            print(' Neuron', n)
            for w in range(len(self.neurons[n].weights)):
                print('  Weight:', self.neurons[n].weights[w])
            print('  Bias:', self.bias)


class Neuron:
    def __init__(self, bias):
        self.bias = bias
        self.inputs = []
        self.weights = []
        self.output = None

    def calculate_output(self, inputs):
        self.inputs = inputs
        self.output = self.sigmoid(self.calculate_total_net_input())
        return self.output

    def calculate_total_net_input(self):
        return sum([self.inputs[j] * self.weights[j] for j in range(len(self.inputs))]) + self.bias

    # 激活函数sigmoid
    @staticmethod
    def sigmoid(total_net_input):
        return 1 / (1 + math.exp(-total_net_input))

    # 计算输出层误差δo1
    def calculate_pd_lsm_sigmoid(self, target_output):
        return self.calculate_pd_least_square_method(target_output) * self.calculate_pd_sigmoid()

    # 每一个神经元的误差是由平方差公式计算的
    def calculate_error(self, target_output):
        return 0.5 * (target_output - self.output) ** 2

    # ∂E / ∂out
    def calculate_pd_least_square_method(self, target_output):
        return -(target_output - self.output)

    # ∂out / ∂net（sigmoid函数的导数）
    def calculate_pd_sigmoid(self) -> float:
        return self.output * (1 - self.output)

    # ∂net / ∂w（前向传播的导数）
    def calculate_pd_feed_forward(self, index):
        return self.inputs[index]
