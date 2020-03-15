import numpy as np
from skimage.external.tifffile import imread

himg = imread("data.tiff")
himg = himg / 2**16

cmf = np.loadtxt("CIE1931-2deg-XYZ.csv",delimiter=",")
cmf = cmf[np.where(cmf[:,0] >= 400)]
cmf = cmf[::2]

