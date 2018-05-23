import torch
import torch.nn as nn


def make_conv_layers(cfg, input_c = 3):
  """ builds the convolution / max pool layers

  The network architecture is provided as a list, containing the
  number of feature maps, or a 'M' for a MaxPooling layer.

  Example for Casia-Net: 
  [32, 64, 'M', 64, 128, 'M', 96, 192, 'M', 128, 256, 'M', 160, 320]

  Parameters
  ----------
  cfg: list
    Configuration for the network (see above)
  input_c: int
    The number of channels in the input (1 -> gray, 3 -> rgb)

  """
  layers = []
  in_channels = input_c
  for v in cfg:
    if v == 'M':
      layers += [nn.MaxPool2d(kernel_size=2, stride=2)]
    else:
      conv2d = nn.Conv2d(in_channels, v, kernel_size=3, padding=1)
      layers += [conv2d, nn.ReLU()]
      in_channels = v
  return nn.Sequential(*layers)

