import numpy as np
import matplotlib.pyplot as plt
import argparse
from PIL import Image


parser = argparse.ArgumentParser(description='Unscramble an image')
parser.add_argument('--input', '-i', default="Messed32.jpg", help='path to input file')
parser.add_argument('--instructions', '-n', help='path to instruction file')
parser.add_argument('--output', '-o', default="Messed32.jpg", help='path to output file')
parser.add_argument('--rows', '-r', default=4,type=int, help='rows')
parser.add_argument('--columns', '-c', default=8,type=int, help='columns')
parser.add_argument('--edges', '-e', default=1,type=int, help='edge thickness')
args = parser.parse_args()

ROWS = args.rows
COLUMNS = args.columns
EDGE_THICKNESS = args.edges

NAME_IN = args.input
NAME_OUT = args.output


img = plt.imread(NAME_IN)
imgH, imgW, imgL = np.shape(img)
segW = round(imgW / COLUMNS)
segH = round(imgH / ROWS)
chunkAr = []

chunkId=0
for i in range(ROWS):
    for j in range(COLUMNS):
        x=j*segW
        y=i*segH
        x2 = x + segW
        y2 = y + segH
        chunk = img[y:y2,x:x2,0:imgL]
        chunkAr.append( {"chunk":chunk,"x":x,"x2":x2,"y":y,"y2":y2,"id":chunkId,"matches":[]})
        chunkId = chunkId + 1

def calculateEdges( chunkTb ):
    chunk = chunkTb["chunk"]
    chunkTb["L"]=chunk[0:segH,0:EDGE_THICKNESS,0:imgL]
    chunkTb["R"]=chunk[0:segH,segW-EDGE_THICKNESS:segW,0:imgL]
    chunkTb["T"]=chunk[0:EDGE_THICKNESS,0:segW,0:imgL]
    chunkTb["B"]=chunk[segH-EDGE_THICKNESS:segH,0:segW,0:imgL]

    #rotate orientation to match top
    chunkTb["R"]=np.rot90(chunkTb["R"], 3)
    chunkTb["B"]=np.rot90(chunkTb["B"], 2)
    chunkTb["L"]=np.rot90(chunkTb["L"], 1)

for chunkTb in chunkAr:
    calculateEdges(chunkTb)
    #plt.figure()
    #plt.imshow(chunk)
    #plt.show()
    
def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])
def mse(imageA, imageB):
    imageA = rgb2gray(imageA).astype("float") 
    imageB = rgb2gray(imageB).astype("float")
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension

    #err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    #err /= float(imageA.shape[0] * imageA.shape[1])

    err = np.square(np.subtract(imageA, imageB)).mean()
    
    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err

def findMatch(index,chunkList,orientationList="LRBT",threshold=500):
    chunkTb = None
    if (type(index)==int):
        chunkTb = chunkList[index]
    else:
        chunkTb = index
        index = -1
    topEdge = chunkTb["T"]
    leftEdge = chunkTb["L"]
    bottomEdge = chunkTb["B"]
    rightEdge = chunkTb["R"]
    orientationAr = orientationList
    if isinstance(orientationAr, str):
        orientationAr = list(orientationAr)
    lastMSE=1000000000000
    tmpMatch=[]
    for j in range(len(chunkList)):
        if (index!=j):
            innerChunk = chunkList[j]
            #does it belong on our right
            if "R" in orientationAr:
                mRightLeft=mse(rightEdge,innerChunk["L"])
                mRightRight=mse(np.rot90(rightEdge,2),innerChunk["R"]) #rot180
                #if (innerChunk["id"]==5 and chunkTb["id"]==2):
                #    print(mRightLeft)
                if (mRightLeft<lastMSE):
                    tmpMatch=[innerChunk["id"],"R","L"] #our right to its left
                    lastMSE=mRightLeft
                if (mRightRight<lastMSE):
                    tmpMatch=[innerChunk["id"],"R","R"] #our right to its left
                    lastMSE=mRightRight
            #does it belong on our left
            if "L" in orientationAr:
                mLeftRight=mse(leftEdge,innerChunk["R"])
                mLeftLeft=mse(np.rot90(leftEdge,2),innerChunk["L"]) #rot180
                if (mLeftRight<lastMSE):
                    tmpMatch=[innerChunk["id"],"L","R"] #our left to its right
                    lastMSE=mLeftRight
                if (mLeftLeft<lastMSE):
                    tmpMatch=[innerChunk["id"],"L","L"] #our left to its right
                    lastMSE=mLeftLeft
            #does it belong on our top
            if "T" in orientationAr:
                mTopBottom=mse(topEdge,innerChunk["B"])
                mTopTop=mse(np.rot90(topEdge,2),innerChunk["T"]) #rot180
                if (mTopBottom<lastMSE):
                    tmpMatch=[innerChunk["id"],"T","B"] #our top to its bottom
                    lastMSE=mTopBottom
                if (mTopTop<lastMSE):
                    tmpMatch=[innerChunk["id"],"T","T"] #our top to its top
                    lastMSE=mTopTop
            #does it belong on our bottom
            if "B" in orientationAr:
                mBottomTop=mse(bottomEdge,innerChunk["T"])
                mBottomBottom=mse(np.rot90(bottomEdge,2),innerChunk["B"]) #rot180
                if (mBottomTop<lastMSE):
                    tmpMatch=[innerChunk["id"],"B","T"] #our bottom to its top
                    lastMSE=mBottomTop
                if (mBottomBottom<lastMSE):
                    tmpMatch=[innerChunk["id"],"B","B"] #our bottom to its bottom
                    lastMSE=mBottomBottom
    tmpMatch.append(lastMSE)
    if lastMSE<=threshold:
        return tmpMatch

def findMatchTL(chunkList,topChunk=None,leftChunk=None,threshold=500):
    bottomEdge = None
    rightEdge = None
    testBottomEdge = False
    testRightEdge = False
    doSquare = False
    tmpMatch=[]
    if not (topChunk is None):
        bottomEdge = topChunk["B"]
        testBottomEdge = True
    if not (leftChunk is None):
        rightEdge = leftChunk["R"]
        testRightEdge = True
    if (testRightEdge and testBottomEdge):
        doSquare = True
    squareFac = 1
    if doSquare:
        squareFac = 2
    lastMSE = 10000000000
    for innerChunk in chunkList:
        if (testRightEdge and innerChunk["id"]==leftChunk["id"]):
            continue
        if (testBottomEdge and innerChunk["id"]==topChunk["id"]):
            continue
        #first, test normal orientation
        combinedMSE = 0
        combinedMSE_Flip = 0
        if testRightEdge:
            combinedMSE = combinedMSE + pow(mse(rightEdge,innerChunk["L"]), squareFac)
            combinedMSE_Flip = combinedMSE_Flip + pow(mse(np.rot90(rightEdge,2),innerChunk["R"]), squareFac)
        if testBottomEdge:
            combinedMSE = combinedMSE + pow(mse(bottomEdge,innerChunk["T"]), squareFac)
            combinedMSE_Flip = combinedMSE_Flip + pow(mse(np.rot90(bottomEdge,2),innerChunk["B"]), squareFac)
        if (testBottomEdge and testRightEdge):
            combinedMSE = pow(combinedMSE,1/squareFac)
            combinedMSE_Flip = pow(combinedMSE_Flip,1/squareFac)
        if (combinedMSE<lastMSE):
            tmpMatch = [innerChunk["id"],"R","L"]
            lastMSE = combinedMSE
        if (combinedMSE_Flip<lastMSE):
            tmpMatch = [innerChunk["id"],"R","R"]
            lastMSE = combinedMSE_Flip
    tmpMatch.append(lastMSE)
    if lastMSE<=threshold:
        return tmpMatch
        
def findChunkById(idv, chunkList):
    for chunk in chunkList:
        if chunk["id"]==idv:
            return chunk

  
#this is going to be third, or 2 in the default Scrambled image
#5 belongs to its right

#top left is 16 on messed32

#topLeftChunkId = int(input())
#topLeftChunk = chunkAr[topLeftChunkId]

chunkSearch = chunkAr.copy()

#chunkSearch.pop(topLeftChunkId)

chunkMap = [None] * ROWS
for i in range(ROWS):
    chunkMap[i]=[None] * COLUMNS

print("Enter row, col, and ID separated by a space.")
print("Enter 'f' without quotes in the same line to mark it as flipped.")
print("Enter a blank line to stop reading.")
knownPairs = []

if not (args.instructions is None):
    instFile = open(args.instructions, "r")
while(True):
    if (args.instructions is None):
        s = input()
    else:
        s=instFile.readline()
        print(s)
    m = map(str, s.split())
    arr = []
    doFlip=False
    for x in m:
        if (x=='f'):
            doFlip=True
        else:
            try:
                arr.append(int(x))
            except ValueError:
                break
    arr.append(doFlip)
    if len(arr)==4:
        knownPairs.append(arr.copy())
    if len(arr)==1:
        break

for pair in knownPairs:
    if len(pair)>3 and pair[3]: #flip it
        matchChunk = findChunkById(pair[2],chunkAr)
        matchChunk["chunk"] = np.rot90(matchChunk["chunk"],2)
        calculateEdges(matchChunk)
    chunkMap[pair[0]][pair[1]]=pair[2]

for colVar in range(COLUMNS):
    for rowVar in range(ROWS):
        val = chunkMap[rowVar][colVar]
        if not (val is None):
            #remove it from list of searchable chunks
            for i in range(len(chunkSearch)):
                chunk = chunkSearch[i]
                if (chunk["id"]==val):
                    chunkSearch.pop(i)
                    break

#start with each column
rowVar = 0
colVar = 0

for colVar in range(COLUMNS):
    for rowVar in range(ROWS):
        chunkId = None
        if not (chunkMap[rowVar][colVar] is None):
            chunkId = chunkMap[rowVar][colVar]
        else:
            topChunk = None
            leftChunk = None
            if (rowVar>0):
                topChunk=findChunkById(chunkMap[rowVar-1][colVar],chunkAr)
            if (colVar>0):
                leftChunk=findChunkById(chunkMap[rowVar][colVar-1],chunkAr)
            if (rowVar==1 and colVar==0):
                print(topChunk["id"])
            match = findMatchTL(chunkSearch,topChunk,leftChunk,100000)
            chunkId = match[0]
            matchChunk = None
            for i in range(len(chunkSearch)):
                chunk = chunkSearch[i]
                if (chunk["id"]==match[0]):
                    matchChunk=chunk
                    chunkSearch.pop(i)
                    break
            if (match[1]==match[2]):
                matchChunk["chunk"] = np.rot90(matchChunk["chunk"],2)
                calculateEdges(matchChunk)
        chunkMap[rowVar][colVar] = chunkId
            
"""
for colVar in range(COLUMNS):
    for rowVar in range(ROWS):
        chunkId = None
        if rowVar==0 and colVar==0:
            chunkId = topLeftChunkId
        else:
            match=None
            if (rowVar==0): #starting a new column
                match=findMatch(leftChunk,chunkSearch,"R",50000)
            else:
                match=findMatch(topChunk,chunkSearch,"B",50000)
            print(match)
            chunkId = match[0]
            matchChunk = None
            for i in range(len(chunkSearch)):
                chunk = chunkSearch[i]
                if (chunk["id"]==match[0]):
                    matchChunk=chunk
                    chunkSearch.pop(i)
                    break
            if (match[1]==match[2]):
                matchChunk["chunk"] = np.rot90(matchChunk["chunk"],2)
                calculateEdges(matchChunk)
            if (rowVar==0): #starting a new column
                leftChunk = matchChunk
            topChunk = matchChunk
        chunkMap[rowVar][colVar] = chunkId
"""

print(chunkMap)
imgFinal = img.copy()

for i in range(ROWS):
    for j in range(COLUMNS):
        chunkId = chunkMap[i][j]
        chunk = findChunkById(chunkId,chunkAr)
        x=j*segW
        y=i*segH
        x2 = x + segW
        y2 = y + segH
        imgFinal[y:y2,x:x2,:]=chunk["chunk"]
        plt.text( (x+x2)/2, (y+y2)/2, str(chunkId))

im = Image.fromarray(imgFinal)
im.save(NAME_OUT)

plt.imshow(imgFinal)
plt.show()

"""
chunkStack = chunkAr.copy()
chunkStackGood=[]
while len(chunkStack)>0:
    match=findMatch(0,chunkStack)
    if (match):
        if (match[1]==match[2]): #if one of the tiles needs to be rotated 180
            #then rotate the match we found
            chunkStack[match[0]]["chunk"] = np.rot90(chunkStack[match[0]]["chunk"],2)
            calculateEdges(chunkStack[match[0]])
        indx = chunkStack[match[0]]["id"] 
        tmpChunk = chunkStack.pop(match[0])
        chunkStack[0]["matches"].append([indx,match[1]])
        chunkStackGood.append(tmpChunk)
    else:
        #print("this chunk is broken")
        #plt.imshow(chunkStack[0]["chunk"])
        #plt.show()
        match=findMatch(0,chunkStackGood)
        if (match[1]==match[2]): #if one of the tiles needs to be rotated 180
            #then rotate the tile we're trying to match
            chunkStack[0]["chunk"] = np.rot90(chunkStack[0]["chunk"],2)
            calculateEdges(chunkStack[match[0]])
            match=findMatch(0,chunkStackGood)
        indx = chunkStack[0]["id"]
        chunkStackGood.append(chunkStack.pop(0))
        tmpChunk = None
        chunkStackGood[match[0]]["matches"].append([indx,match[2]])
        print("no match on chunk")
        chunkStackGood.append(chunkStack.pop(0))
for chunk in chunkStackGood:
    print(chunk["id"])
    print(chunk["matches"])
"""

#for chunk in chunkAr:    