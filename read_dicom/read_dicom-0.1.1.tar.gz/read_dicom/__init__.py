import numpy as np
import dicom

# Heavily inspired from a 2009 scrit by Daniel Nanz:
# http://code.google.com/p/pydicom/source/browse/
# source/dicom/contrib/pydicom_Tkinter.py?
# r=f2c30464fd3b7e553af910ee5a9f5bcf4b3f4ccf
def window_level(arr, window_center, window_width, lut_min=0, lut_max=255):

    # Basic sanity checking.
    if np.isreal(arr).sum() != arr.size: raise ValueError
    if lut_max != 255: raise ValueError
    if arr.dtype != np.float64: arr = arr.astype(np.float64)

    # Get window information.
    window_width = max(1, window_width)
    wc, ww = np.float64(window_center), np.float64(window_width)
    lut_range = np.float64(lut_max) - lut_min

    # Transform the image.
    minval = wc - 0.5 - (ww - 1.0) / 2.0
    maxval = wc - 0.5 + (ww - 1.0) / 2.0
    min_mask = (minval >= arr)
    to_scale = (arr > minval) & (arr < maxval)
    max_mask = (arr >= maxval)
    if min_mask.any(): arr[min_mask] = lut_min

    # Scale the image to the right proportions.
    if to_scale.any(): arr[to_scale] = \
      ((arr[to_scale] - (wc - 0.5)) /
      (ww - 1.0) + 0.5) * lut_range + lut_min
    if max_mask.any(): arr[max_mask] = lut_max

    arr = np.rint(arr).astype(np.uint8)

    return arr

# Read in a DICOM file.
def read_dcm(file_name):
  data = dicom.read_file(file_name)
  arr = data.pixel_array.astype(np.float64)
  
  # Rescale image.
  if ('RescaleIntercept' in data) and ('RescaleSlope' in data):
    intercept = int(data.RescaleIntercept)
    slope = int(data.RescaleSlope)
    arr = slope * arr + intercept
    
  wc = (arr.max() + arr.min()) / 2.0
  ww = arr.max() - arr.min() + 1.0
  
  if ('WindowCenter' in data) and ('WindowWidth' in data):
    wc = data.WindowCenter
    ww = data.WindowWidth
    try: wc = wc[0]
    except: pass
    try: ww = ww[0]
    except: pass
  
  pixel_spacing = data.PixelSpacing
  
  return { 
    "hounsfield": np.copy(arr), 
    "grayscale": window_level(arr, wc, ww),
    "pixel_spacing": pixel_spacing
  }