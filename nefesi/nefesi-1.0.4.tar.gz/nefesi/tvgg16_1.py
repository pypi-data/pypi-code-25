
import pickle


from utils.image import ImageDataset
from keras.applications.vgg16 import VGG16, preprocess_input


def main():

    dataset = '/home/oprades/ImageNet/train/' # dataset path
    save_path = '/home/oprades/oscar/'
    layer_names = ['block1_conv1', 'block1_conv2',
                   'block2_conv1', 'block2_conv2',
                   'block3_conv1', 'block3_conv2', 'block3_conv3']

    model = VGG16()

    my_net = pickle.load(open(save_path + 'block1_3.obj', 'rb'))
    my_net.model = model
    img_dataset = ImageDataset(dataset, (224, 224), preprocess_input)
    my_net.dataset = img_dataset

    for l in my_net.get_layers():
        i = 0
        neuron_idx = []
        for f in l.get_filters():
            tmp = f.get_size_patches(my_net, l)

            i = i + tmp
        print l.get_layer_id(), i







if __name__ == '__main__':
    import os


    # os.environ["CUDA_VISIBLE_DEVICES"] = "0"


    main()
