import  sys, os, pdb, shutil, datetime as dt, pandas as pd, numpy as np, cv2, matplotlib.pyplot as plt

from skimage    import io, color, measure, draw, img_as_bool
from scipy      import optimize
from time       import sleep
from math       import cos, sin, radians, floor

basePath    = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( basePath + '/Libraries' )

import image_fns as imgFns

######################
######  INPUTS  ######
######################
thetas          = [0, 90, 180, 270]
video_dir       = r'C:\Users\danie\Dropbox\Projects\Fellyjish\Vidz\Frames'

######################
######  DO IT   ######
######################
all_vid_dirs    = os.listdir( video_dir )
all_ts          = [ ]
for idx, dir in enumerate( all_vid_dirs ):
    print( ' >> Computing distances for video ' + str( idx ) + ' of ' + str( len( all_vid_dirs ) ) )
    this_frame_dir  = video_dir + '\\' + dir
    ts              = imgFns.process_video( this_frame_dir, thetas = thetas)
    ts['file']      = dir
    all_ts.append( ts )
print(pd.concat(all_ts))
