import  sys, os, pdb, shutil, datetime as dt, pandas as pd, numpy as np, cv2, matplotlib.pyplot as plt, webcolors, floweaver as fw

from skimage            import io, color, measure, draw, img_as_bool
from scipy              import optimize, signal
from time               import sleep
from math               import cos, sin, radians, floor
from bisect             import bisect
from ipysankeywidget    import SankeyWidget

basePath    = os.path.dirname( os.path.dirname( __file__ ) )
sys.path.append( basePath + '\Libraries' )

import image_fns as imgFns

######################
######  INPUTS  ######
######################
# thetas          = [0, 45, 90, 135, 180, 225, 270, 315]
thetas          = list( range( 0, 360, 45 ) )
theta_rollup    = list( range( 0, 361, 45 ) )
#video_dir       = os.path.dirname( basePath ) + '\Vidz\Frames'
video_dir       = r'E:\20190130'
specific_vids   = [ '20190130_827pm'] #pass the name of the folder in which the frames sit (no extension and no path location, just simple file name)
# specific_vids   = [ '20190114_01', '20190114_02' ] #pass the name of the folder in which the frames sit (no extension and no path location, just simple file name)

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
    print( ' >> Computing distances for video ' + str( idx + 1 ) + ' of ' + str( len( all_vid_dirs ) ) )
    this_frame_dir  = video_dir + '\\' + dir
    ts              = imgFns.process_video( this_frame_dir, thetas = thetas )
    ts['Avg']       = ts.mean( axis = 1 )
    ts['file']      = dir
    all_ts.append( ts )

    #using the average line, estimate the pulse interval
    # peaks           = signal.find_peaks(ts['Avg'], prominence = 3, distance = 20, height = peak_min)[0].tolist()
    valleys           = signal.find_peaks([ 1/x for x in ts['Avg'].tolist()], distance = 20, height = np.percentile( [1/x for x in ts['Avg'].tolist()], 75 ))[0].tolist()

    #tag each timestamp for which pulse its in
    ts['pulse_index'] = [ bisect( valleys, x ) for x in ts.index.tolist() ]

    print( '  >> Getting peaks...' )
    peaks               = ts[[ x for x in ts.columns.values if x not in ['Avg', 'file'] ]].groupby( 'pulse_index' ).agg( imgFns.pulse_init )
    peaks['init']       = peaks.apply( lambda x: imgFns.first_init( x.tolist() ), axis=1)
    peaks               = peaks[peaks['init'].apply( lambda x: not pd.isnull(x) )]
    peaks['init']       = peaks['init'].apply( lambda x: peaks.columns[int(x)] if x is not None else None)
        
    peaks['init_agg']   = [ str( theta_rollup[bisect( theta_rollup, int(x) ) - 1] ) + ' - ' + str( theta_rollup[bisect( theta_rollup, int(x) )] ) for x in peaks['init'].tolist() ]
    peaks['file']       = dir
    first_pulses.append( peaks.reset_index() )

ts              = pd.concat( all_ts ).reset_index()
ts.to_csv( os.path.dirname( basePath ) + '\Jellies\Results\Pulse Data\Time Series\Time_Series.csv', index = False )

#aggregate first pulses and tack on which came first in the next 2 pulses for sankey diagram
first_pulses                    = pd.concat( first_pulses )
cols                            = first_pulses.columns.tolist() + [ 'init_agg_next', 'init_agg_next_next' ]

first_pulses['next_index']      = first_pulses['pulse_index'] - 1
first_pulses['next_next_index'] = first_pulses['pulse_index'] - 2

first_pulses                    = first_pulses.merge( first_pulses[['next_index', 'file', 'init_agg']], left_on = ['pulse_index', 'file'], right_on = ['next_index', 'file'], how = 'left', copy = False, suffixes = ['', '_next'] )
first_pulses                    = first_pulses.merge( first_pulses[['next_next_index', 'file', 'init_agg']], left_on = ['pulse_index', 'file'], right_on = ['next_next_index', 'file'], how = 'left', copy = False, suffixes = ['', '_next_next'] )
first_pulses                    = first_pulses[ cols ]

first_pulses.to_csv( os.path.dirname( basePath ) + '\Jellies\Results\Pulse Data\First Pulse\Pulse_Order.csv', mode = 'w+', index = False )

#make the sankey chart
pulse_transition            = first_pulses[['file', 'init_agg', 'init_agg_next', 'pulse_index']].groupby(['file', 'init_agg', 'init_agg_next']).count().reset_index()
pulse_transition.columns    = ['file', 'source', 'target', 'value']
sankey_data                 = pulse_transition[ [ 'source', 'target', 'value'] ]
sankey_data.to_csv( os.path.dirname( basePath ) + '\Jellies\Results\Pulse Data\First Pulse\sankey.csv', mode = 'w+', index = False )
print( sankey_data )

pulses      = first_pulses['init_agg'].tolist()
streaks     = { key: [ ] for key in set( pulses ) }
this_streak = 1
for indx, pulse in enumerate( pulses ):
    if( (indx+1) == len( first_pulses ) ):
        break
    if( pulse == pulses[indx + 1] ):
        this_streak+=1
    else:
        streaks[ pulse ].append( this_streak )
        this_streak = 1
streaks_df  = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in streaks.items() ]))
print( streaks_df )
streaks_df.to_csv( os.path.dirname( basePath ) + '\Jellies\Results\Pulse Data\Streaks\streaks.csv', mode = 'w+', index = False )
