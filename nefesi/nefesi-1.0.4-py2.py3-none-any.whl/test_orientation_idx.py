import pickle

import numpy as np

from network_data import NetworkData
from utils.image import ImageDataset
from keras.applications.vgg16 import VGG16
from read_activations import get_activation_from_pos

def main():

    dataset = '/data/local/datasets/ImageNet/train/' # dataset path
    save_path = '/data/115-1/users/oscar/'
    layer_names = ['block1_conv2']
    num_max_activations = 100


    model = VGG16()

    # my_net = NetworkData(model, layer_names, dataset, num_max_activations=num_max_activations, save_path=save_path)
    # my_net.eval_network(1000, (224, 224), batch_size=100, preprocessing_function=norm_input)
    # my_net.save()


    my_net = pickle.load(open(save_path + 'vgg16_layer1.obj', 'rb'))
    my_net.model = model
    img_dataset = ImageDataset(dataset, (224, 224), norm_input)
    my_net.dataset = img_dataset
    my_net.save_path = save_path


    f = my_net.get_layers()[0].get_filters()[0]
    f.print_params()
    act = f.get_activations()
    loc = f.get_locations()
    img_n = f.get_images_id()

    img = my_net.dataset.load_images(img_n)

    print get_activation_from_pos(img, model, layer_names[0], 0, loc)







if __name__ == '__main__':
    import os
    os.environ["CUDA_VISIBLE_DEVICES"] = "0"

    avg_img = np.load('nefesi/external/averageImage.npy')

    def norm_input(x):
        return x-avg_img

    main()
