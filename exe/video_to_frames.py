import sys, os

basePath    = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( basePath + '/Libraries' )

inPath  = r'C:\Users\danie\Dropbox\Projects\Fellyjish\Vidz'
inFile  = inPath + '\Day_hr1-4pm-_jelly1-500frames.avi'
outPath = inPath + '\Frames'

import image_fns as img

img.video_to_frames( inFile, outPath )