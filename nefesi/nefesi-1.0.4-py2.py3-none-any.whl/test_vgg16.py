
import pickle

import numpy as np

from network_data import NetworkData
from utils.image import ImageDataset
from keras.applications.vgg16 import VGG16, preprocess_input

def main():

    dataset = '/data/local/datasets/ImageNet/train/' # dataset path
    save_path = '/data/115-1/users/oscar/'
    layer_names = ['block1_conv2', 'block2_conv2']




    # for evaluate a new model
    model = VGG16()
    my_net = NetworkData(model)
    my_net.eval_network(dataset, layer_names,
                        save_path, target_size=(224, 224), batch_size=100,
                        preprocessing_function=preprocess_input)

    # for load the data previously saved in save_path
    my_net = NetworkData.load_from_disk("path to results",
                                        model_file="path to model file")

    # my_net = pickle.load(open(save_path + 'vgg16.obj', 'rb'))
    # my_net.model = model
    # img_dataset = ImageDataset(dataset, (224, 224), norm_input)
    # my_net.dataset = img_dataset
    # my_net.save_path = save_path
    #
    #
    #
    #
    # sel_idx = my_net.selectivity_idx(['color'], layer_names)
    # my_net.save()
    # my_net.model = model
    # my_net.dataset = img_dataset
    #
    # sel_idx = my_net.selectivity_idx(['orientation'], layer_names)
    # my_net.save()
    # my_net.model = model
    # my_net.dataset = img_dataset
    #
    # sel_idx = my_net.selectivity_idx(['symmetry'], layer_names)
    # my_net.save()
    # my_net.model = model
    # my_net.dataset = img_dataset
    #

    labels = pickle.load(open('nefesi/external/labels_imagenet.obj', 'rb'))
    sel_idx = my_net.selectivity_idx(['class'], layer_names, labels=labels)


    # my_net.save()
    # my_net.model = model
    # my_net.dataset = img_dataset
    #
    # sim_idx = my_net.similarity_index(layer_names)
    # my_net.save()





if __name__ == '__main__':
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    avg_img = np.load('nefesi/external/averageImage.npy')

    def norm_input(x):
        return x-avg_img

    main()
