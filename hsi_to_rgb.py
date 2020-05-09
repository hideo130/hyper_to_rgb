import numpy as np
from pathlib import Path
from PIL import Image


def load_light_distribution(name="lamp_spectrum.csv"):
    sd_light_source = np.loadtxt(name, skiprows=1, dtype="float")
    sd_light_source = sd_light_source[np.where(sd_light_source[:, 0] >= 400)]
    # rindx = np.where(sd_light_source[:, 0] >= 400) and np.where(sd_light_source[:, 0] <= 600)
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
    # sd_light_source = sd_light_source / np.max(sd_light_source)
    sd_light_source = sd_light_source[::2]
    sd_light_source = sd_light_source[:44]
    # print(sd_light_source)
    return sd_light_source


def hsi_to_ci31931_rgb(himg, dist_name):
    pass


def hsi_to_rgb(himg, dist_name):
    """
    input: ハイパースペクトル画像　HSI（numpy型）
    return: RGB画像（Image objedct）
    """
    # 計測時にノイズとして負の値になった値を0にする
    np.where(himg < 0, 0, himg)

    cmf = np.loadtxt("./csvs/CIE1931-2deg-XYZ.csv", delimiter=",")
    # HSIが400nm以上のため等色関数も400nm以上のみを利用
    cmf = cmf[np.where(cmf[:, 0] >= 400)]
    # 光源の分光分布の5nm刻みをHSIと同じ10nm刻みに変更
    cmf = cmf[::2]
    cmf = cmf[:44, :]

    stem = Path(dist_name).stem
    if stem in ["A"]:
        # 標準光源Aは780nmまでを可視光としているため，HSIと等色関数も780nmm以下に制限
        nhimg = himg[:, :, :39]
        cmf = cmf[:39, :]
        sd_light_source = load_illuminantA(name=dist_name)
    elif stem in ["D65"]:
        nhimg = himg[:, :, :44]
        cmf = cmf[:44, :]
        sd_light_source = load_illuminantA(name=dist_name)
    else:
        nhimg = himg[:, :, :44]
        sd_light_source = load_light_distribution(name=dist_name)

    flag_const_100 = True
    ncmf = cmf[:, 1:]
    nmf_multi_ld = ncmf * sd_light_source
    x = nmf_multi_ld[:, 0]
    y = nmf_multi_ld[:, 1]
    z = nmf_multi_ld[:, 2]
    if flag_const_100:
        k = 100 / np.sum(y)
        # print(np.sum(y))
    else:
        k = 1 / np.sum(y)
        # print(np.sum(y))
    X = np.sum(x * nhimg, axis=2)
    Y = np.sum(y * nhimg, axis=2)
    Z = np.sum(z * nhimg, axis=2)
    XYZ = np.stack([X, Y, Z], 2)
    # print(np.max(XYZ), np.min(XYZ))
    # print(np.max(Y*k), np.min(Y*k))
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
        # HSI画像配布元と同じガンマ補正（ガンマ=0.6）をする
        # print(np.max(rgb_img2))
        rgb_img2 = np.power(rgb_img2/255, 0.6)
    else:
        # XYZからsRGBへのレンダリングするためのガンマ補正
        # print(np.max(255*rgb_img2))
        rgb_img2 = np.where(rgb_img2 <= 0.0031308, 12.92 * rgb_img2, 1.055 * np.power(rgb_img2, 1/2.4) - 0.055)

    if flag_const_100:
        img = Image.fromarray(np.uint8(255*rgb_img2))
    else:
        img = Image.fromarray(np.uint8(255*rgb_img2))
    return img
