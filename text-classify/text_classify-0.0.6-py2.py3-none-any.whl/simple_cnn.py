import torch
from torch import nn

from text_classify.utils import load_embedding


class SimpleCNN(nn.Module):
    # def __init__(self, embedding_model, embedding_dim, vocab_size, index2word, embedding_format,
    #         embedding_train, filter_num, filter_size, sentence_length, class_num):
    def __init__(self, args):
        super(SimpleCNN, self).__init__()

        print('=> Init embedding layer')
        if args.cut:
            vocab_size = args.word_vocab_size
            sentence_length = args.word_sentence_length
        else:
            vocab_size = args.char_vocab_size
            sentence_length = args.char_sentence_length

        self.embedding = nn.Embedding(vocab_size, args.embedding_dim, sentence_length)
        # embedding_weight = load_embedding(embedding_model, index2word, vocab_size,
        #                                   embedding_dim, embedding_format)
        # embedding_weight = torch.from_numpy(embedding_weight).type(torch.FloatTensor)
        # self.embedding.weight = nn.Parameter(embedding_weight)
        # self.embedding.weight.requires_grad = False

        print('=> Init model layer')
        self.relu = nn.ReLU(inplace=True)
        self.conv = nn.ModuleList([
            self.conv_relu_bn_pool(args.embedding_dim, args.num_filter, size, sentence_length)
            for size in args.filter_size
        ])
        self.hidden_dim = len(args.filter_size) * args.filter_num
        self.bn = nn.BatchNorm1d(self.hidden_dim)
        self.fc = nn.Linear(self.hidden_dim, args.num_class)

    def conv_relu_bn_pool(self, in_channel, out_channel, kernel_size, dim):
        return nn.Sequential(
            nn.Conv1d(in_channel, out_channel, kernel_size),
            self.relu,
            nn.BatchNorm1d(out_channel),
            nn.MaxPool1d(dim - kernel_size + 1),
        )

    def forward(self, input_data):
        embeded = self.embedding(input_data).transpose(1, 2)
        hidden = torch.cat([
            conv(embeded) for conv in self.conv
        ], 2)
        hidden = self.bn(hidden.view(-1, self.hidden_dim))
        return self.fc(hidden)
