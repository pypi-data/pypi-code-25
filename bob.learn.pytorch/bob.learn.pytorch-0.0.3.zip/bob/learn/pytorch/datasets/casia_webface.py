#!/usr/bin/env python
# encoding: utf-8

import os

import numpy

from torch.utils.data import Dataset, DataLoader

import bob.io.base
import bob.io.image

from .utils import map_labels


class CasiaWebFaceDataset(Dataset):
  """Casia WebFace dataset (for CNN training).
  
  Class representing the CASIA WebFace dataset

  **Parameters**

  root-dir: path
    The path to the data

  frontal_only: boolean
    If you want to only use frontal faces 
    
  transform: torchvision.transforms
    The transform(s) to apply to the face images
  """
  def __init__(self, root_dir, transform=None, start_index=0):
    self.root_dir = root_dir
    self.transform = transform
    self.data_files = []
    id_labels = []

    for root, dirs, files in os.walk(self.root_dir):
      for name in files:
        filename = os.path.split(os.path.join(root, name))[-1]
        path = root.split(os.sep)
        subject = int(path[-1])
        self.data_files.append(os.path.join(root, name))
        id_labels.append(subject)
 
    self.id_labels = map_labels(id_labels, start_index)

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
    sample = {'image': image, 'label': identity}

    if self.transform:
      sample = self.transform(sample)

    return sample


class CasiaDataset(Dataset):
  """Casia WebFace dataset.
  
  Class representing the CASIA WebFace dataset

  **Parameters**

  root-dir: path
    The path to the data

  frontal_only: boolean
    If you want to only use frontal faces 
    
  transform: torchvision.transforms
    The transform(s) to apply to the face images
  """
  def __init__(self, root_dir, frontal_only=False, transform=None, start_index=0):
    self.root_dir = root_dir
    self.transform = transform
  
    dir_to_pose_label = {'l90': '0',
                       'l75': '1',
                       'l60': '2',
                       'l45': '3',
                       'l30': '4',
                       'l15': '5',
                       '0'  : '6',
                       'r15': '7',
                       'r30': '8',
                       'r45': '9',
                       'r60': '10',
                       'r75': '11',
                       'r90': '12',
                      }

    # get all the needed file, the pose labels, and the id labels
    self.data_files = []
    self.pose_labels = []
    id_labels = []

    for root, dirs, files in os.walk(self.root_dir):
      for name in files:
        filename = os.path.split(os.path.join(root, name))[-1]
        path = root.split(os.sep)
        subject = int(path[-1])
        cluster = path[-2]
        self.data_files.append(os.path.join(root, name))
        self.pose_labels.append(int(dir_to_pose_label[cluster]))
        id_labels.append(subject)
 
    self.id_labels = map_labels(id_labels, start_index)
      
    
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
    sample = {'image': image, 'label': identity, 'pose': pose}

    if self.transform:
      sample = self.transform(sample)

    return sample
