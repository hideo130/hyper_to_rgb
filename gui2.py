import PySimpleGUI as sg
from PIL import Image
import io

# img = Image.open("~/ubuntu/homework/img_pros3/Hyperspectral_to_rgb_image/Encastre 10_1cm.PNG")
img = Image.open("Encastre 10_1cm.PNG")
bio = io.BytesIO()
img.save(bio, format="PNG")
img = bio.getvalue()
# return bio.getvalue()

layout = [
    # [sg.Image(img.tobytes("raw"))]
    [sg.Image(data=img)]
]

window = sg.Window('住所を入力', layout)

while True:
    event, values = window.read()

    if event is None:
        print('exit')
        break


window.close()
