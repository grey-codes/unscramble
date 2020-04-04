import numpy as np
import matplotlib.pyplot as plt

ROWS = 2
COLUMNS = 4

img = plt.imread("Messed.jpg")
imgH, imgW, imgL = np.shape(img)
segW = round(imgW / COLUMNS)
segH = round(imgH / ROWS)
chunkAr = []

for i in range(ROWS):
    for j in range(COLUMNS):
        x=j*segW
        y=i*segH
        x2 = x + segW
        y2 = y + segH
        chunk = img[y:y2,x:x2,0:imgL]
        chunkAr.append( {"chunk":chunk,"x":x,"x2":x2,"y":y,"y2":y2})
for chunkTb in chunkAr:
    chunk = chunkTb["chunk"]
    chunkTb["L"]=chunk[0:segH,0:1,0:imgL]
    chunkTb["R"]=chunk[0:segH,segW-1:segW,0:imgL]
    chunkTb["T"]=chunk[0:1,0:segW,0:imgL]
    chunkTb["B"]=chunk[segH-1:segH,0:segW,0:imgL]

    #rotate orientation to match top
    chunkTb["R"]=np.rot90(chunkTb["R"], 3)
    chunkTb["B"]=np.rot90(chunkTb["B"], 2)
    chunkTb["L"]=np.rot90(chunkTb["L"], 1)
    #plt.figure()
    #plt.imshow(chunk)
    #plt.show()
    
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])
def mse(imageA, imageB):
    imageA = rgb2gray(imageA)
    imageB = rgb2gray(imageB)
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err
def findMatch(index,chunkList,uniqueMatch):
    chunkTb = chunkList[index]
    topEdge = chunkTb["T"]
    leftEdge = chunkTb["L"]
    bottomEdge = chunkTb["B"]
    rightEdge = chunkTb["R"]
    lastMSE=1000000000000
    doFlip=True
    tmpMatch=[]
    for j in range(len(chunkAr)):
        if (index!=j):
            innerChunk = chunkAr[j]
            if not (uniqueMatch and "match" in innerChunk):
                #does it belong on our right
                mRightLeft=mse(rightEdge,innerChunk["L"])
                mRightRight=mse(np.rot90(rightEdge,2),innerChunk["R"]) #rot180
                if (mRightLeft<lastMSE):
                    tmpMatch=[j,"R","L"] #our right to its left
                    lastMSE=mRightLeft
                if (mRightRight<lastMSE):
                    tmpMatch=[j,"R","R"] #our right to its left
                    lastMSE=mRightRight
                #does it belong on our left
                mLeftRight=mse(leftEdge,innerChunk["R"])
                mLeftLeft=mse(np.rot90(leftEdge,2),innerChunk["L"]) #rot180
                if (mLeftRight<lastMSE):
                    tmpMatch=[j,"L","R"] #our left to its right
                    lastMSE=mLeftRight
                if (mLeftLeft<lastMSE):
                    tmpMatch=[j,"L","L"] #our left to its right
                    lastMSE=mLeftLeft
                #does it belong on our top
                mTopBottom=mse(topEdge,innerChunk["B"])
                mTopTop=mse(np.rot90(topEdge,2),innerChunk["T"]) #rot180
                if (mTopBottom<lastMSE):
                    tmpMatch=[j,"T","B"] #our top to its bottom
                    lastMSE=mTopBottom
                if (mTopTop<lastMSE):
                    tmpMatch=[j,"T","T"] #our top to its top
                    lastMSE=mTopTop
                #does it belong on our bottom
                mBottomTop=mse(bottomEdge,innerChunk["T"])
                mBottomBottom=mse(np.rot90(bottomEdge,2),innerChunk["B"]) #rot180
                if (mBottomTop<lastMSE):
                    tmpMatch=[j,"B","T"] #our bottom to its top
                    lastMSE=mBottomTop
                if (mBottomBottom<lastMSE):
                    tmpMatch=[j,"B","B"] #our bottom to its bottom
                    lastMSE=mBottomBottom
    tmpMatch.append(lastMSE)
    if (lastMSE<1000):
        chunkTb["match"] = tmpMatch
    else:
        chunkTb["root"] = True
    #print(tmpMatch)
            
    
for i in range(len(chunkAr)):
    findMatch(i,chunkAr,True)
#for chunk in chunkAr:    