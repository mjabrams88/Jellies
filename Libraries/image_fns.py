import sys, os, pdb, shutil, datetime as dt, pandas as pd, numpy as np, cv2, time

from skimage    import io, color, measure, draw, img_as_bool
from scipy      import optimize
from time       import sleep
from math       import cos, sin, radians, floor

# import scipy.signal
import matplotlib.pyplot as plt
# from matplotlib import cm
# import skimage.io
# import cv2
# import pandas as pd

###### A whole bunch of skimage stuff
# import skimage.feature
# import skimage.filter
# import skimage.filter.rank
# import skimage.io
# import skimage.morphology
# import skimage.restoration
# import skimage.segmentation

def video_to_frames(input_loc, output_loc):
    """Function to extract frames from input video file
    and save them as separate frames in an output directory.
    Args:
        input_loc: Input video file.
        output_loc: Output directory to save the frames.
    Returns:
        None
    """
    try:
        os.mkdir(output_loc)
    except OSError:
        pass
    # Log the time
    time_start = time.time()
    # Start capturing the feed
    cap = cv2.VideoCapture(input_loc)
    # Find the number of frames
    video_length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) - 1
    print ("Number of frames: ", video_length)
    count = 0
    print ("Converting video..\n")
    # Start converting the video
    while cap.isOpened():
        # Extract the frame
        ret, frame = cap.read()
        # Write the results back to output location.
        cv2.imwrite(output_loc + "/%#05d.jpg" % (count+1), frame)
        count = count + 1
        # If there are no more frames left
        if (count > (video_length-1)):
            # Log the time again
            time_end = time.time()
            # Release the feed
            cap.release()
            # Print stats
            print ("Done extracting frames.\n%d frames extracted" % count)
            print ("It took %d seconds forconversion." % (time_end-time_start))
            break

def locateContours( img ):
    ## (1) Read
    # img = cv2.imread("img04.png")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    ## (2) Threshold
    th, threshed = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV|cv2.THRESH_OTSU)

    ## (3) Find the first contour that greate than 100, locate in centeral region
    ## Adjust the parameter when necessary
    cnts = cv2.findContours(threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts = sorted(cnts, key=cv2.contourArea)
    H,W = img.shape[:2]
    for cnt in cnts:
        x,y,w,h = cv2.boundingRect(cnt)
        if cv2.contourArea(cnt) > 100 and (0.7 < w/h < 1.3) and (W/4 < x + w//2 < W*3/4) and (H/4 < y + h//2 < H*3/4):
            break

    ## (4) Create mask and do bitwise-op
    mask = np.zeros(img.shape[:2],np.uint8)
    cv2.drawContours(mask, [cnt],-1, 255, -1)
    dst = cv2.bitwise_and(img, img, mask=mask)

    ## Display it
    # cv2.imwrite("dst.png", dst)
    # cv2.imshow("dst.png", dst)
    # cv2.waitKey()
    
    return( dst )
    
def createLineIterator(P1, P2, img):
    """
    Produces and array that consists of the coordinates and intensities of each pixel in a line between two points

    Parameters:
        -P1: a numpy array that consists of the coordinate of the first point (x,y)
        -P2: a numpy array that consists of the coordinate of the second point (x,y)
        -img: the image being processed

    Returns:
        -it: a numpy array that consists of the coordinates and intensities of each pixel in the radii (shape: [numPixels, 3], row = [x,y,intensity])     
    """
    #define local variables for readability
    imageH = img.shape[0]
    imageW = img.shape[1]
    P1X = P1[0]
    P1Y = P1[1]
    P2X = P2[0]
    P2Y = P2[1]

    #difference and absolute difference between points
    #used to calculate slope and relative location between points
    dX = P2X - P1X
    dY = P2Y - P1Y
    dXa = np.abs(dX)
    dYa = np.abs(dY)

    #predefine numpy array for output based on distance between points
    # itbuffer = np.empty(shape=(np.maximum(dYa,dXa),3),dtype=np.float32)
    itbuffer = np.empty(shape=(np.maximum(dYa,dXa),2),dtype=np.float32)  
    itbuffer.fill(np.nan)

    #Obtain coordinates along the line using a form of Bresenham's algorithm
    negY = P1Y > P2Y
    negX = P1X > P2X
    if P1X == P2X: #vertical line segment
        itbuffer[:,0] = P1X
        if negY:
            itbuffer[:,1] = np.arange(P1Y - 1,P1Y - dYa - 1,-1)
        else:
            itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)              
    elif P1Y == P2Y: #horizontal line segment
        itbuffer[:,1] = P1Y
        if negX:
            itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
        else:
            itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
    else: #diagonal line segment
        steepSlope = dYa > dXa
        if steepSlope:
            slope = dX.astype(np.float32)/dY.astype(np.float32)
            if negY:
                itbuffer[:,1] = np.arange(P1Y-1,P1Y-dYa-1,-1)
            else:
                itbuffer[:,1] = np.arange(P1Y+1,P1Y+dYa+1)
            itbuffer[:,0] = (slope*(itbuffer[:,1]-P1Y)).astype(np.int) + P1X
        else:
            slope = dY.astype(np.float32)/dX.astype(np.float32)
            if negX:
                itbuffer[:,0] = np.arange(P1X-1,P1X-dXa-1,-1)
            else:
                itbuffer[:,0] = np.arange(P1X+1,P1X+dXa+1)
            itbuffer[:,1] = (slope*(itbuffer[:,0]-P1X)).astype(np.int) + P1Y

    #Remove points outside of image
    colX = itbuffer[:,0]
    colY = itbuffer[:,1]
    itbuffer = itbuffer[(colX >= 0) & (colY >=0) & (colX<imageW) & (colY<imageH)]

    #Get intensities from img ndarray
    # itbuffer[:,2] = img[itbuffer[:,1].astype(np.uint),itbuffer[:,0].astype(np.uint)][:,0]

    return( itbuffer )
    

def get_coord( theta ):
    theta_raw   = theta
    assert( theta < 360 )
    quad    = floor( theta / 90 )
    theta   = theta % 90
    h       = 480 / 2
    # w       = 640 / 2
    if( quad == 0 ):
        x   = h * sin( radians( theta ) )
        x   = x + h
        y   = h * cos( radians( theta ) )
        y   = h - y
    elif( quad == 1 ):
        x   = h * cos( radians( theta ) )
        x   = x + h
        y   = -h * sin( radians( theta ) )
        y   = h + (-y)
    elif( quad == 2 ):
        x   = -h * sin( radians( theta ) )
        x   = h + x
        y   = -h * cos( radians( theta ) )
        y   = h + (-y)
    else:
        x   = -h * cos( radians( theta ) )
        x   = h + x
        y   = h * sin( radians( theta ) )
        y   = h - y
    return( (theta_raw, x, y) ) #pixels are from the top left

def process_video( frame_dir, thetas= [0, 90, 180, 270]):
    centers     = [ ]
    centers_x   = [ ]
    centers_y   = [ ]
    
    coordinates = [ get_coord(x) for x in thetas ]
    jellyadii   = { str(k): [ ] for k in thetas }
    files       = os.listdir( frame_dir )
    for N, file in enumerate( files ):
        if(N % 100 == 0):
            print( '  ++ Frame ' + str(N) + ' of ' + str( len( files ) ) )
        img             = io.imread(frame_dir + '\\' + file)
        regions         = measure.regionprops(img)
        this_center     = regions[len(regions)-1].centroid[:2]
        this_center_x   = int( this_center[1] )
        this_center_y   = int( this_center[0] )

        centers.append( this_center )
        centers_x.append( this_center_x )
        centers_y.append( this_center_y )
        
        # img_clean   = locateContours ( img )
        # use a rolling average center here?
        if( N == 1 ):
            this_img = img.copy()
            for coordinate in coordinates:
                line        = createLineIterator( np.array([this_center_x, this_center_y]), np.array([int(coordinate[1]),int(coordinate[2])]), this_img )    
                for indx, pt in enumerate( line ):
                    this_img[int(pt[1]), int(pt[0])] = [ 255, 0, 0 ]
            plt.imshow(this_img)
            plt.draw()
            plt.pause(5) # pause how many seconds
            plt.close()

        for coordinate in coordinates:        
            line        = createLineIterator( np.array([this_center_x, this_center_y]), np.array([int(coordinate[1]),int(coordinate[2])]), img )
            for indx, pt in enumerate( line ):
                gradient    = img[int(pt[1]), int(pt[0])][0]
                if( gradient < 50 ):
                    jellyadii[str(coordinate[0])].append( indx )
                    break
    return( pd.DataFrame( jellyadii ) )
