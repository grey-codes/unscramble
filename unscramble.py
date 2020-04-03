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
		print(np.shape(chunk))
		chunkAr.append( {"chunk":chunk})
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
	print(np.shape(chunkTb["T"]))
	print(np.shape(chunkTb["B"]))
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

edges = ["L","R","T","B"]

for i in range(len(chunkAr)):
	chunkTb = chunkAr[i]
	topEdge = chunkTb["T"]
	leftEdge = chunkTb["L"]
	matchTop = [-1,"T"]
	matchLeft = [-1,"L"]
	lastTopMSE = 200000000
	lastLeftMSE = 200000000
	for j in range(len(chunkAr)):
		if (i!=j):
			innerChunk = chunkAr[j]
			mTopTop=mse(topEdge,innerChunk["T"])
			mTopBottom=mse(topEdge,innerChunk["B"])
			mLeftLeft=mse(leftEdge,innerChunk["L"])
			mLeftRight=mse(leftEdge,innerChunk["R"])
			if mLeftLeft < lastLeftMSE:
				lastLeftMSE = mLeftLeft
				matchLeft = [j,"L"]
			if mLeftRight < lastLeftMSE:
				lastLeftMSE = mLeftRight
				matchLeft = [j,"R"]
			if mTopTop < lastTopMSE:
				lastTopMSE = mTopTop
				matchTop = [j,"T"]
			if mTopBottom < lastTopMSE:
				lastTopMSE = mTopBottom
				matchTop = [j,"B"]
	chunkTb["matchLeft"] = matchLeft
	print(str(i)+" matchLeft: " + str(matchLeft[0]) + " -- " + matchLeft[1],end=" [")
	print(lastLeftMSE,end="]\n")
		