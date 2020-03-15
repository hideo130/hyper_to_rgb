import PySimpleGUI as sg
from PIL import Image

layout = [
    [sg.Image("LyteProLPF2.PNG")]
]

window = sg.Window('住所を入力', layout)

while True:
    event, values = window.read()

    if event is None:
        print('exit')
        break


window.close()
