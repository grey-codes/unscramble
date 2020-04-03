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
for chunkTb in chunkAr:
    chunk = chunkTb["chunk"]
    chunkTb["L"]=chunk[0:1,0:segH,0:imgL]
    chunkTb["R"]=chunk[segW-1:segW,0:segH,0:imgL]
    chunkTb["T"]=chunk[0:segW,0:1,0:imgL]
    chunkTb["B"]=chunk[0:segW,segH-1:segH,0:imgL]

    #rotate orientation to match top
    chunkTb["R"]=np.rot90(chunkTb["R"], 3)
    chunkTb["B"]=np.rot90(chunkTb["B"], 2)
    chunkTb["L"]=np.rot90(chunkTb["L"], 1)
