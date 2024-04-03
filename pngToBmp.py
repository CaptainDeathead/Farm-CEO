from PIL import Image
import os
import sys

def pngToBmp(image):
    path = os.getcwd() + '/'
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            im = Image.open(path + filename)
            im.save(path + filename[:-4] + '.bmp')
            print(filename + ' is converted to ' + filename[:-4] + '.bmp')
    print('All png files are converted to bmp files')

if __name__ == '__main__':
    pngToBmp(sys.argv[1])