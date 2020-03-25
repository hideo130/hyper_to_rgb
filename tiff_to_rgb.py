import numpy as np
from skimage.external.tifffile import imread
from pathlib import Path
from PIL import Image


def load_light_distribution(name="lamp_spectrum.csv"):
    sd_light_source = np.loadtxt(name, skiprows=1, dtype="float")
    sd_light_source = sd_light_source[np.where(sd_light_source[:, 0] >= 400)]
    # rindx = np.where(sd_light_source[:, 0] >= 400) and np.where(sd_light_source[:, 0] <= 600)
    # sd_light_source[rindx] = 0.01
    sd_light_source = sd_light_source[:, 1:2]
    # print("sum", np.sum(sd_light_source))
    sd_light_source = sd_light_source[::20]
    sd_light_source = sd_light_source[:44]
    # print(sd_light_source.shape)
    return sd_light_source


def load_illuminantA(name="A.csv"):
    sd_light_source = np.loadtxt(name, skiprows=1, dtype="float")
    sd_light_source = sd_light_source[np.where(sd_light_source[:, 0] >= 400)]
    sd_light_source = sd_light_source[:, 1:2]
    # print("sum",np.sum(sd_light_source))
    sd_light_source = sd_light_source / np.max(sd_light_source)
    sd_light_source = sd_light_source[::2]
    sd_light_source = sd_light_source[:44]
    # print(sd_light_source)
    return sd_light_source


def tiff_to_rgb(himg):
    """
    input: ハイパースペクトル画像（numpy型）
    return: RGB画像（Image objedct）
    """
    # 計測時にノイズとして負の値になった値を0にする
    np.where(himg < 0, 0, himg)

    cmf = np.loadtxt("CIE1931-2deg-XYZ.csv", delimiter=",")
    # 分光画像が400nm以上のため400nm以上のデータを利用する
    cmf = cmf[np.where(cmf[:, 0] >= 400)]
    # 光源の分光分布が5nm刻みで得られているから，10nm刻みに変更する
    cmf = cmf[::2]
    cmf = cmf[:44, :]

    # name = "./Pictures.csv"
    name = "./D65.csv"
    # name = "./A.csv"
    # name = "./Twister.csv"

    stem = Path(name).stem
    if stem in ["A"]:
        nhimg = himg[:, :, :39]
        cmf = cmf[:39, :]
        sd_light_source = load_illuminantA(name=name)
    elif stem in ["D65"]:
        nhimg = himg[:, :, :44]
        cmf = cmf[:44, :]
        sd_light_source = load_illuminantA(name=name)
    else:
        nhimg = himg[:, :, :44]       
        sd_light_source = load_light_distribution(name=name)

    flag_const_100 = True
    ncmf = cmf[:, 1:]
    nmf_multi_ld = ncmf * sd_light_source
    x = nmf_multi_ld[:, 0]
    y = nmf_multi_ld[:, 1]
    z = nmf_multi_ld[:, 2]
    if flag_const_100:
        k = 100 / np.sum(y)
    else:
        k = 1 / np.sum(y)
    X = np.sum(x * nhimg, axis=2)
    Y = np.sum(y * nhimg, axis=2)
    Z = np.sum(z * nhimg, axis=2)
    XYZ = np.stack([X, Y, Z], 2)
    XYZ = XYZ * k
    XYZ.shape
    xyz_to_r = np.array([3.2406255, -1.537208, -0.4986286])
    r = np.dot(XYZ, xyz_to_r)
    xyz_to_g = np.array([-0.9689307, 1.8757561, 0.0415175])
    g = np.dot(XYZ, xyz_to_g)
    xyz_to_b = np.array([0.0557101, -0.2040211, 1.0569959])
    b = np.dot(XYZ, xyz_to_b)
    rgb_img2 = np.stack([r, g, b], axis=2)

    rgb_img2 = np.where(rgb_img2 < 0, 0, rgb_img2)
    if flag_const_100:
        rgb_img2 = np.power(rgb_img2/255, 0.6) * 255
    else:
        rgb_img2 = np.where(rgb_img2 <= 0.0031308, 12.92 * rgb_img2, 1.055 * np.power(rgb_img2, 1/2.4) - 0.055)

    if flag_const_100:
        img = Image.fromarray(np.uint8(rgb_img2))
    else:
        img = Image.fromarray(np.uint8(255*rgb_img2))
    return img
