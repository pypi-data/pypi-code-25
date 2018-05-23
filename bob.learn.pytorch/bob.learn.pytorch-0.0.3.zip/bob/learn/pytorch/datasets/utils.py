#!/usr/bin/env python
# encoding: utf-8

import numpy

import torchvision.transforms as transforms

class FaceCropper():
  """
    Class to crop a face, based on eyes position
  """
  def __init__(self, cropped_height, cropped_width):
    # the face cropper
    from bob.bio.face.preprocessor import FaceCrop
    cropped_image_size = (cropped_height, cropped_width)
    right_eye_pos = (cropped_height // 5, cropped_width // 4 -1)
    left_eye_pos = (cropped_height // 5, cropped_width // 4 * 3)
    cropped_positions = {'leye': left_eye_pos, 'reye': right_eye_pos}
    self.face_cropper = FaceCrop(cropped_image_size=cropped_image_size,
                                 cropped_positions=cropped_positions,
                                 color_channel='rgb',
                                 dtype='uint8'
                                )

  def __call__(self, sample):
    cropped = self.face_cropper(sample['image'], sample['eyes'])
    sample['image'] = cropped
    return sample
  

class RollChannels(object):
  """
    Class to transform a bob image into skimage.
    i.e. CxHxW to HxWxC
  """
  def __call__(self, sample):
    temp = numpy.rollaxis(numpy.rollaxis(sample['image'], 2),2)
    sample['image'] = temp
    return sample

class ToTensor(object):
  def __init__(self):
    self.op = transforms.ToTensor()
  
  def __call__(self, sample):
    sample['image'] = self.op(sample['image'])
    return sample

class Normalize(object):
  def __init__(self, mean, std):
    self.op = transforms.Normalize(mean, std)

  def __call__(self, sample):
    sample['image'] = self.op(sample['image'])
    return sample

class Resize(object):
  def __init__(self, size):
    self.op = transforms.Resize(size)

  def __call__(self, sample):
    # convert to PIL image
    from PIL.Image import fromarray
    img = fromarray(sample['image'].squeeze())
    img = self.op(img)
    sample['image'] = numpy.array(img)
    sample['image'] = sample['image'][..., numpy.newaxis]
    return sample


def map_labels(raw_labels, start_index=0):
  """
  Map the ID label to [0 - # of IDs] 
  """
  possible_labels = list(set(raw_labels))
  labels = numpy.array(raw_labels)
  
  for i in range(len(possible_labels)):
    l = possible_labels[i]
    labels[numpy.where(labels==l)[0]] = i + start_index 

  # -----
  # map back to native int, resolve the problem with dataset concatenation
  # it does: line 78 is now ok
  # for some reason, it was not working when the type of id labels were numpy.int64 ...
  labels_int = []
  for i in range(len(labels)):
    labels_int.append(labels[i].item())
  
  return labels_int


from torch.utils.data import Dataset
import bob.io.base
import bob.io.image


class ConcatDataset(Dataset):
  """
  Class to concatenate two or more datasets for DR-GAN training

  **Parameters**

  datasets: list
    The list of datasets (as torch.utils.data.Dataset)
  """
  def __init__(self, datasets):
    
    self.transform = datasets[0].transform
    self.data_files = sum((d.data_files for d in datasets), [])
    self.pose_labels = sum((d.pose_labels for d in datasets), [])
    self.id_labels = sum((d.id_labels for d in datasets), [])
  
  def __len__(self):
      """
        return the length of the dataset (i.e. nb of examples)
      """
      return len(self.data_files)


  def __getitem__(self, idx):
      """
        return a sample from the dataset
      """
      image = bob.io.base.load(self.data_files[idx])
      identity = self.id_labels[idx]
      pose = self.pose_labels[idx]
      sample = {'image': image, 'id': identity, 'pose': pose}

      if self.transform:
        sample = self.transform(sample)

      return sample


