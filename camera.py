from functions import get_config
from PIL import Image
import requests


def main():
    config = get_config()
    print(f"grabbing picture from {config['settings']['cam_path']}")
    img = Image.open(requests.get(config['settings']['cam_path'], stream=True).raw)
    print('The format of img is: ', img.format)
    print('The mode of img is: ', img.mode)
    print('The size of img is: ', img.size)
    print('The palette of img is: ', img.palette)
    print('The info of img is: ', img.info)
    resizedImage = img.resize((176, 184))
    resizedImage = resizedImage.convert()
    print(Image.Exif())
    resizedImage.show()

    # format to rgb 565

    # send data to switch


main()
