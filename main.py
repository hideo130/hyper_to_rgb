import PySimpleGUI as sg
from PIL import Image
import io
import numpy as np
from skimage.external.tifffile import imread
from hsi_to_rgb import hsi_to_rgb
from get_sd_fig import get_sd_fig
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
from logging import getLogger, INFO, basicConfig
import japanize_matplotlib
matplotlib.use('Agg')

# japanize_matplotlibはimportするだけでmatplotlibで日本語が使えるようになる．
# flake8を満たすためだけの記述．
japanize_matplotlib


def call_img(img):
    """
    input img:Image object
    return img:画像のbytes型
    sg.ImageはPNGかGIFしか読み込むことができない．
    レンダリングしたpng画像やハイパースペクトル画像のpng形式のbytes型を作成し，
    その後，sg.Imageの引数dataに渡すことで画像を表示している．
    """
    bio = io.BytesIO()
    # バッファに画像を出力
    img.save(bio, format="PNG")
    # バッファの全内容の bytes型 をgetvalue()で取得する
    img = bio.getvalue()
    return img


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


do_debug = True
if do_debug:
    basicConfig(level=INFO)
logger = getLogger(__name__)

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
    logger.info(event)
    if event in (None, 'Quit'):
        print('exit')
        break
    elif event == "__SLIDER__":
        logger.info(values)
        tmp = int(values["__SLIDER__"])
        img = Image.fromarray(np.uint8(himg[:, :, tmp]*255))
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("%d nm ~ %d nmを表示" % (400+10*tmp, 400+10*(tmp+1)))
        logger.info("update img")
    elif event == "Rendering":
        img = hsi_to_rgb(himg, load_name)
        display_name = values["__DIST__"]
        # img.save("results/%s_k=1.png" % (display_name))
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("レンダリング画像を表示")

    elif event == "__DIST__":
        display_name = values["__DIST__"]
        load_name = disp_name_to_load_name[display_name]
        logger.info(load_name)
        img = hsi_to_rgb(himg, load_name)
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("レンダリング画像を表示")
        axes.cla()
        figure, axes = get_sd_fig(display_name, load_name=load_name, axes=axes)
        fig_canvas_agg.draw()
window.close()
