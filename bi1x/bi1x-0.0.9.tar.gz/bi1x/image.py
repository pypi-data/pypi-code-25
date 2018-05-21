import numpy as np

import skimage.io
import skimage.measure

from matplotlib import path

class SimpleImageCollection(object):
    """
    Load a collection of images.

    Parameters
    ----------
    load_pattern : string or list
        If string, uses glob to generate list of files containing
        images. If list, this is the list of files containing images.
    load_func : callable, default skimage.io.imread
        Function to be called to load images.
    conserve_memory : bool, default True
        If True, do not load all images into RAM. If False, load
        all into a list.

    Returns
    -------
    ic : SimpleImageCollection instance
        ic[n] gives image n of the image collection.

    Notes
    -----
    .. Any keyword arguments except those listed above are passed into
    load_func as kwargs.
    .. This is a much simplified (and therefore faster) version of
    skimage.io.ImageCollection.
    """

    def __init__(self, load_pattern, load_func=skimage.io.imread,
                 conserve_memory=True, **load_func_kwargs):
        if isinstance(load_pattern, str):
            self.fnames = glob.glob(load_pattern)
        else:
            self.fnames = load_pattern

        self.conserve_memory = conserve_memory

        if self.conserve_memory:
            self.load_func = load_func
            self.kwargs = load_func_kwargs
        else:
            self.ims = [load_func(f, **load_func_kwargs) for f in self.fnames]



    def __getitem__(self, n):
        """
        Return selected image.
        """
        if self.conserve_memory:
            return self.load_func(self.fnames[n], **self.load_func_kwargs)
        else:
            return self.ims[n]


def simple_image_collection(im_glob, load_func=skimage.io.imread,
                            conserve_memory=True, **load_func_kwargs):
    """
    Load a collection of images.

    Parameters
    ----------
    load_pattern : string or list
        If string, uses glob to generate list of files containing
        images. If list, this is the list of files containing images.
    load_func : callable, default skimage.io.imread
        Function to be called to load images.
    conserve_memory : bool, default True
        If True, do not load all images into RAM. If False, load
        all into a list.

    Returns
    -------
    ic : SimpleImageCollection instance
        ic[n] gives image n of the image collection.

    Notes
    -----
    .. Any keyword arguments except those listed above are passed into
    load_func as kwargs.
    .. This is a much simplified (and therefore faster) version of
    skimage.io.ImageCollection.
    """
    return SimpleImageCollection(im_glob, load_func=load_func,
                                 conserve_memory=conserve_memory,
                                 **load_func_kwargs)


def verts_to_roi(verts, shape, shift=True):
    """
    Converts list of vertices to an ROI and ROI bounding box

    Parameters
    ----------
    verts : array_like, shape (n_verts, 2)
        List of vertices of a polygon with no crossing lines.  The units
        describing the positions of the vertices are interpixel spacing.
    shape : 2-tuple of ints
        Shape of image, (n_rows, n_columns).
    shift : bool, default True
        If True, consider the center of a pixel as being half-integers.
        This is useful if using a polygon drawn over an image, since the
        image is "plotted" with pixels represented as squares centered
        on half-integer pixel values.

    Returns
    -------
    roi : array_like, Boolean, shape
        roi[i,j] is True if pixel (i,j) is in the ROI.
        roi[i,j] is False otherwise
    roi_bbox : tuple of slice objects
        To get a subimage with the bounding box of the ROI, use
        im[roi_bbox].
    roi_box : array_like, shape is size of bounding box or ROI
        A mask for the ROI with the same dimension as the bounding
        box.  The indexing starts at zero at the upper right corner
        of the box.
    """

    # Ranges to search
    i_range = (int(verts[:,0].min()), int(verts[:,0].max()) + 1)
    j_range = (int(verts[:,1].min()), int(verts[:,1].max()) + 1)
    sub_i_size = i_range[1] - i_range[0]
    sub_j_size = j_range[1] - j_range[0]

    # Set up points we want to check in subimage
    i = np.arange(*i_range)
    j = np.arange(*j_range)
    ii, jj = np.meshgrid(i, j)
    pts = np.array(list(zip(ii.ravel(), jj.ravel())))

    # Make a path object from vertices
    p = path.Path(verts)

    # Get list of points that are in roi
    if shift:
        in_roi = p.contains_points(pts + 0.5)
    else:
        in_roi = p.contains_points(pts)

    # Subimage ROI
    sub_roi = in_roi.reshape((sub_j_size, sub_i_size)).astype(np.bool)

    # Build full ROI
    roi = np.zeros(shape, dtype=bool)
    roi[j_range[0]:j_range[1], i_range[0]:i_range[1]] = sub_roi

    # Get bounding box of ROI
    regions = skimage.measure.regionprops(roi.astype(np.int))
    bbox = regions[0].bbox
    roi_bbox = np.s_[bbox[0]:bbox[2] + 1, bbox[1]:bbox[3] + 1]

    # Get ROI mask for just within bounding box
    roi_box = roi[roi_bbox]

    # Return boolean in same shape as image
    return roi, roi_bbox, roi_box
