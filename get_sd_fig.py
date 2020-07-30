import colour
import numpy as np
from colour import SpectralDistribution


def load_light_distribution(name="lamp_spectrum.csv"):
    sd_light_source = np.loadtxt(name, skiprows=1, dtype="float")
    sd_light_source = sd_light_source[np.where(sd_light_source[:, 0] >= 400)]
    return sd_light_source


def get_sd_fig(disp_name, load_name, axes=None):
    """

    fig, axes  = colour.plotting.plot_single_sd(sd, standalone=False)
    """
    sd_light_source = load_light_distribution(name=load_name)
    # print(sd_light_source[:5,0])
    sd = SpectralDistribution(sd_light_source[:, 1], domain=sd_light_source[:, 0],  name=disp_name)
    # sd = SpectralDistribution(sd_light_source, name='Sample')
    # print(type(fig), type(axes))
    if axes:
        return colour.plotting.plot_single_sd(sd, cmfs='CIE 1964 10 Degree Standard Observer', axes=axes, standalone=False)
    else:
        return colour.plotting.plot_single_sd(sd, cmfs='CIE 1964 10 Degree Standard Observer', standalone=False)
