from PIL import Image
import os
import sys

def pngToBmp(imagePath):
    path = imagePath + '/'
    for filename in os.listdir(path):
        if filename.endswith('.png'):
            im = Image.open(path + filename)
            im.save(path + filename[:-4] + '.bmp')
            print(filename + ' is converted to ' + filename[:-4] + '.bmp')
    pathInfo = list(os.walk(path))
    for i in range(1, len(pathInfo)):
        print(pathInfo[i][0])
        pngToBmp(pathInfo[i][0])
    print('All png files are converted to bmp files')

if __name__ == '__main__':
    pngToBmp(os.getcwd() + '/' + sys.argv[1])