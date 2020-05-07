import PySimpleGUI as sg
from PIL import Image
import io
import numpy as np
from skimage.external.tifffile import imread
from tiff_to_rgb import tiff_to_rgb
from get_sd_fig import get_sd_fig
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
import japanize_matplotlib
matplotlib.use('Agg')


def call_img(img):
    """
    input img:Image object
    return img:画像のbytes型
    """
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    img = bio.getvalue()
    return img


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


himg = imread("./data/data.tiff")
himg = himg / 2**16
himg = himg[::2, ::2, :]
img = Image.fromarray(np.uint8(himg[:, :, 0]*255))
img = call_img(img)
disp_name_to_load_name = {"標準光源D65": "./csvs/D65.csv", '標準光源A': "./csvs/A.csv",
                          "光源A": "./csvs/Pictures.csv", "光源B": "./csvs/LightScience.csv"}
load_name = "./csvs/D65.csv"
figure, axes = get_sd_fig(disp_name="標準光源D65", load_name=load_name)
figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds


layout = [
    [sg.Frame("Menu", [
        [sg.T("400 nm ~ 410 nmを表示", key="_SHOW_",
              size=(25, 1), font=('Helvetica 20'))],
        [sg.Slider(range=(0, 60), orientation='h', enable_events=True,
                   size=(34, 20), key='__SLIDER__', default_value=0)],
        [sg.Combo(('標準光源D65', '標準光源A', "光源A", "光源B"), key="__DIST__", default_value='標準光源D65',
                  enable_events=True, size=(20, 1)), sg.Button("Rendering"), sg.Quit()],
        [sg.Canvas(size=(figure_w, figure_h), key='canvas')]
    ]),
        sg.Image(data=img,  key='_OUTPUT_')],

]


window = sg.Window('sRGBをレンダリング', layout, finalize=True)
fig_canvas_agg = draw_figure(window['canvas'].TKCanvas, figure)


while True:
    event, values = window.read()
    # print(event)
    if event in (None, 'Quit'):
        print('exit')
        break
    elif event == "__SLIDER__":
        # print(values[0])
        tmp = int(values["__SLIDER__"])
        img = Image.fromarray(np.uint8(himg[:, :, tmp]*255))
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("%d nm ~ %d nmを表示" % (400+10*tmp, 400+10*(tmp+1)))
        # print("update img")
    elif event == "Rendering":
        img = tiff_to_rgb(himg, load_name)
        display_name = values["__DIST__"]
        # img.save("results/%s_k=1.png" % (display_name))
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("レンダリング画像を表示")

    elif event == "__DIST__":
        display_name = values["__DIST__"]
        load_name = disp_name_to_load_name[display_name]
        print(load_name)
        img = tiff_to_rgb(himg, load_name)
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("レンダリング画像を表示")
        axes.cla()
        figure, axes = get_sd_fig(display_name, load_name=load_name, axes=axes)
        fig_canvas_agg.draw()
window.close()
