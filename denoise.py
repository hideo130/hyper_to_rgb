import numpy as np


def calculate_std(reshaped_img):
    pass


class Dnoise:
    def __init__(self, img) -> None:
        self.img = img

    def denoise_svd(self):
        shape = self.img.shape
        reshape = shape[0] * shape[1], shape[3]

        reshaped_img = np.reshape(self.img, reshape)
        mean = np.mean(reshaped_img, axis=1)
        std = np.einsum("ij, ij -> iij", reshaped_img - mean, reshaped_img - mean)
        # np.linalg.svd()
