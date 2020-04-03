import numpy as np

import matplotlib.pyplot as plt

ROWS = 4
COLUMNS = 8

img = plt.imread("Messed32.jpg")
imgH, imgW, imgL = np.shape(img)
segW = imgW // COLUMNS
segH = imgH // ROWS
chunkAr = []

for i in range(ROWS):
    for j in range(COLUMNS):
        x=i*segW
        y=j*segH
        x2 = x + segW
        y2 = y + segH
        chunk = img[x:x2,y:y2,0:imgL]
        chunkAr.append( {"chunk":chunk})
