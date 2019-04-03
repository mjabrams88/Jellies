import  sys, os, pdb, shutil, datetime as dt, pandas as pd, numpy as np

from skimage            import io, color, measure, draw, img_as_bool	#scikit-image
from scipy              import optimize, signal
from time               import sleep
from math               import cos, sin, radians, floor
from bisect             import bisect
from ipysankeywidget    import SankeyWidget

basePath    = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( basePath + '\Libraries' )

import image_fns as imgFns
import excel_fns as xlFns

######################
######  INPUTS  ######
######################
thetas              = list( range( 0, 360, 5 ) )
theta_rollup        = list( range( 0, 361, 45 ) )
#video_dir          = os.path.dirname( basePath ) + '\Vidz\Frames'
#video_dir           = r'E:\20190131\Vidz\Frames'
video_dir          = r'I:\20190205\Frames'
#video_dir          = r'I:\20190201\Frames'

#specific_vids       = [  ] #pass the name of the folder in which the frames sit (no extension and no path location, just simple file name)
specific_vids        = [ '20190205_240pm' ]
#specific_vids      = [ '20190201_631pm' ]
min_pulse_length    = 10    #frames
#min_pulse_length    = 10
garbageCollect      = False

######################
######  DO IT   ######
######################
if( len( specific_vids ) ):
    all_vid_dirs    = specific_vids
else:
    all_vid_dirs    = os.listdir( video_dir )
all_ts          = [ ]
first_pulses    = [ ]

for idx, dir in enumerate( all_vid_dirs ):
    if( '.' in dir ): continue

    print( ' >> Computing distances for video ' + str( idx + 1 ) + ' of ' + str( len( all_vid_dirs ) ) )
    this_frame_dir  = video_dir + '\\' + dir
    files       = os.listdir( this_frame_dir )
    files       = [ f for f in files if f not in [ 'outputs' ] ]                            #only process frames. remove other stuff

    nFrames     = 100000
    chunks      = [files[i:(i + nFrames)] for i in range(0, len(files), nFrames)]

    output  = { 'First_Pulse':      [ ],    #frames at which pulse initiated
                'First_Pulse_Rank': [ ],    #rank of the pulse initiation
                'RollUp':           [ ],
                'RollUp_Rank':      [ ],
              }
    for chunkNumber, chunk in enumerate( chunks ):
        ts              = imgFns.process_video( this_frame_dir, files = chunk, thetas = thetas )
        ts['Avg']       = ts.mean( axis = 1 )

        #using the average line, estimate the pulse interval
        # peaks           = signal.find_peaks(ts['Avg'], prominence = 3, distance = 20, height = p eak_min)[0].tolist()
        valleys           = signal.find_peaks([ 1/x for x in ts['Avg'].tolist()], distance = min_pulse_length, height = np.percentile( [1/x for x in ts['Avg'].tolist()], 75 ))[0].tolist()
        #tag each timestamp for which pulse its in
        ts['pulse_index'] = [ bisect( valleys, x ) for x in ts.index.tolist() ]

        print( '  >> Getting pulse initiations...' )
        pulses      = ts[[ x for x in ts.columns.values if x not in ['Avg'] ]].groupby( 'pulse_index' ).agg( imgFns.pulse_init )
        pulse_order = pulses.apply( lambda x: imgFns.init_order( x.tolist() ), axis=1).reset_index()

        col_groups  = [ bisect( theta_rollup, int(x) ) for x in pulses.columns.values ]

        rollup        = { }
        for group in set(col_groups):
            cols            = [ pulses.columns.values[indx] for indx, col in enumerate( col_groups ) if col == group ]
            rollup[ 'rollup_' + str(group) ]   = pulses[cols].mean( axis = 1 )
            # rollup[ 'rollup_' + str(group) ]   = pulses[cols].min( axis = 1 )

        rollup                  = ((pd.DataFrame( rollup )*2).round(0)/2)                           #adjust the rounding here to encourage / discourage ties
        rollup_order            = rollup.apply( lambda x: imgFns.init_order( x.tolist() ), axis=1)
        rollup_order.columns    = rollup.columns
        rollup_order.reset_index( inplace = True )

        output['First_Pulse'].append( pulses + chunkNumber*nFrames)
        output['First_Pulse_Rank'].append( pulse_order )
        output['RollUp'].append( rollup + chunkNumber*nFrames )
        output['RollUp_Rank'].append( rollup_order )
        print( pulses[:25] + chunkNumber*nFrames )

xlFns.to_excel( { k: pd.concat(v) for k, v in output.items() },
                file                    = os.path.dirname( basePath ) + '\Results\First Pulse\\FP_' + dir.replace(' ', '_') + '.xlsx',
                masterFile              = os.path.dirname( basePath ) + '\Results\First Pulse\Pulse_Order_vMaster.xlsx',
                allowMasterOverride     = True,
                promptIfLocked          = True,
                xlsxEngine              = 'xlwings', #xlsxwriter, openpyxl
                closeFile               = True,
        )

if( garbageCollect ):
    os.remove( os.path.dirname(basePath) + '\Results\Time Series\inProgress' )