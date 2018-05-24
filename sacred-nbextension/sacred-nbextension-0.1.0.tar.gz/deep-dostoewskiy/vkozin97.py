
# coding: utf-8

# In[ ]:

import theano
import lasagne


# In[ ]:

text = open('dostoewskij.txt').read().lower()


# In[5]:

#эти две строчки нужно запустить один раз после установки пакета nltk

# import nltk
# nltk.download('punkt')

import nltk.data

tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
sentences = tokenizer.tokenize(text)

from nltk.tokenize import word_tokenize
tokenized = word_tokenize(text)

tokenized_sentences = [word_tokenize(s) for s in sentences]


# In[11]:

sentences[10:15]


# In[ ]:

import gensim
w2v = gensim.models.Word2Vec(tokenized_sentences, size=200, min_count=0)
d = set(tokenized) - set(w2v.wv.vocab.keys())
tokenized = [x for x in tokenized if not (x in d)]
vec_tokenized = [w2v[x] for x in tokenized]



def sample_random_batches(source, n_batches=10, seq_len=20):
    X_batch, y_batch = np.zeros((n_batches, seq_len, w2v.vector_size)), np.zeros((n_batches, w2v.vector_size))

    for i in range(n_batches):
        pos = np.random.randint(0, len(source) - seq_len - 1)
        X_batch[i, :] = source[pos:pos+seq_len]
        y_batch[i] = source[pos+seq_len]
    return X_batch, y_batch


# In[6]:

seq_length = 15
w2v.vector_size == 200
input_sequence = T.tensor3('input sequence','float32')
target_values = T.matrix('target y')


# In[5]:

network = lasagne.layers.InputLayer(shape=(None,seq_length, w2v.vector_size), input_var=input_sequence)
#network = lasagne.layers.EmbeddingLayer(network, input_size=len(tokens), output_size=len(tokens), W=np.eye(len(tokens)))
print(network.output_shape)
#network = lasagne.layers.LSTMLayer(network, num_units=seq_length * 5, grad_clipping=grad_clip, only_return_final=False)
#print(network.output_shape)
#network = lasagne.layers.LSTMLayer(network, num_units=seq_length*8, grad_clipping=grad_clip, only_return_final=True)
#print(network.output_shape)
network = lasagne.layers.DenseLayer(network, num_units=100, nonlinearity=lasagne.nonlinearities.rectify)
print(network.output_shape)
#network = lasagne.layers.LSTMLayer(network, num_units=50, grad_clipping=grad_clip)
#print(network.output_shape)
network = lasagne.layers.DenseLayer(network, num_units=200, nonlinearity=lasagne.nonlinearities.sigmoid)
print(network.output_shape)
network = lasagne.layers.DenseLayer(network, num_units=100, nonlinearity=lasagne.nonlinearities.tanh)
print(network.output_shape)
network = lasagne.layers.DenseLayer(network, num_units=w2v.vector_size, nonlinearity=lasagne.nonlinearities.linear)
print(network.output_shape)
l_out = network

weights = lasagne.layers.get_all_params(l_out,trainable=True)

prediction = lasagne.layers.get_output(l_out)
numerator = theano.tensor.sum(prediction*target_values, axis=1)
denominator = theano.tensor.sqrt(theano.tensor.sum(prediction**2, axis=1)*theano.tensor.sum(target_values**2, axis=1))
#loss = lasagne.objectives.squared_error(prediction, target_values).mean()
loss = (0.5 - numerator / denominator / 2).mean()
updates = lasagne.updates.adagrad(loss, weights)

test_prediction = lasagne.layers.get_output(l_out, deterministic=True)
#test_loss = lasagne.objectives.categorical_crossentropy(test_prediction, target_values).mean()
numerator = theano.tensor.sum(test_prediction*target_values, axis=1)
denominator = theano.tensor.sqrt(theano.tensor.sum(test_prediction**2, axis=1)*theano.tensor.sum(target_values**2, axis=1))
test_loss = (0.5 - numerator / denominator / 2).mean()


# In[ ]:

#обучение
train = theano.function([input_sequence, target_values], loss, updates=updates, allow_input_downcast=True)

#функция потерь без обучения
compute_cost = theano.function([input_sequence, target_values], test_loss, allow_input_downcast=True)

# Вероятности с выхода сети
probs = theano.function([input_sequence], prediction, allow_input_downcast=True)


times = []
losses_mean = []
losses_std = []

from time import clock

print("Training ...")

#сколько всего эпох
n_epochs=30

#сколько цепочек обрабатывать за 1 вызов функции обучения
batch_size=10

# раз в сколько эпох печатать примеры 
batches_per_epoch = 1000

for epoch in range(n_epochs):
    t = clock()
    #print("Генерируем текст в пропорциональном режиме")
    #prop_texts.append(generate_sample(proportional_sample_fun,None))
    
    #print("Генерируем текст в жадном режиме (наиболее вероятные буквы)")
    #max_texts.append(generate_sample(max_sample_fun,None))

    costs = []
    
    for _ in range(batches_per_epoch):
        
        x,y = sample_random_batches(vec_tokenized, batch_size, seq_length)
        costs.append(train(x, y))
        
    losses_mean.append(np.mean(costs))
    losses_std.append(np.std(costs))
    times.append(clock() - t)

