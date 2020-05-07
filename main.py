import PySimpleGUI as sg
from PIL import Image
import io
import numpy as np
from skimage.external.tifffile import imread
from tiff_to_rgb import tiff_to_rgb


def call_img(img):
    """
    input img:Image object
    return img:画像のbytes型
    """
    bio = io.BytesIO()
    img.save(bio, format="PNG")
    img = bio.getvalue()
    return img


himg = imread("data2.tiff")
himg = himg / 2**16
img = Image.fromarray(np.uint8(himg[:, :, 0]*255))
img = call_img(img)

# img = Image.open("A.PNG")

layout = [
    # [sg.Image(img.tobytes("raw"))]
    # [sg.Button('Check'), sg.Quit()],
    [sg.Quit()],
    [sg.T("Show 1 channel.", key="_SHOW_", size=(25, 1), font=('Helvetica 20')),
     sg.Slider(range=(0, 60), orientation='h',enable_events=True,
               size=(34, 20), key='__SLIDER__', default_value=0)
     ],
    [sg.Button("Rendering")],
    [sg.Image(data=img,  key='_OUTPUT_')],

]

window = sg.Window('sRGBをレンダリング', layout)

while True:
    event, values = window.read()
    print(event)
    if event in (None, 'Quit'):
        print('exit')
        break
    elif event == "__SLIDER__":
        # print(values[0])
        tmp = int(values["__SLIDER__"])
        img = Image.fromarray(np.uint8(himg[:, :, tmp]*255))
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("Show %d channel." % (int(tmp)))
        print("update img")
    elif event == "Rendering":
        img = tiff_to_rgb(himg)
        img = call_img(img)
        window['_OUTPUT_'].update(data=img)
        window["_SHOW_"].update("Show sRGB image.")

window.close()
