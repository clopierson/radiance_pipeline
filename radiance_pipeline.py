import os
import sys
import platform

from pathlib import Path

import time


from radiance_pipeline.radiance_data import RadianceData

from radiance_pipeline.logs import *


rp = __import__(__name__)

def radiance_pipeline( sessionData ):
  global radiance_pipeline_percent
  radiance_pipeline_percent = 0

  # Grab time pipeline session started for log filenames, only want 1 per session
  sessionTime = time.strftime("%Y%m%d-%H%M%S")

  # Get OS Platform info
  osName = os.name
  osSystem = platform.system()
  osRelease = platform.release()
  osVersion = platform.version()

  print( "OS Name: {}".format( osName ) )
  print( "OS System: {}".format( osSystem ) )
  print( "OS Release: {}".format( osRelease ) )
  print( "OS Version: {}".format( osVersion ) )
  print( "\n" )


  # Apply different merging logic
  TEST_MODE_ON = False

  # Ensure temp directory exists for storing intermediate output files from each pipeline step
  Path( sessionData.path_temp ).mkdir( mode=0o755, parents=True, exist_ok=True )

  # Joining paths for intermediate file results with absolute path of temp directory: cross-platform filepaths
  output1Path = os.path.join( sessionData.path_temp, "output1.hdr" )
  output2Path = os.path.join( sessionData.path_temp, "output2.hdr" )
  output3Path = os.path.join( sessionData.path_temp, "output3.hdr" )
  output4Path = os.path.join( sessionData.path_temp, "output4.hdr" )
  output5Path = os.path.join( sessionData.path_temp, "output5.hdr" )
  output6Path = os.path.join( sessionData.path_temp, "output6.hdr" )
  output7Path = os.path.join( sessionData.path_temp, "output7.hdr" )
  output8Path = os.path.join( sessionData.path_temp, "output8.hdr" )
  output9Path = os.path.join( sessionData.path_temp, "output9.hdr" )
  output10Path = os.path.join( sessionData.path_temp, "output10.hdr" )


  # List of paths
  intermediateOutputFilePaths = [ output1Path, output2Path, output3Path, output4Path, output5Path,
                                  output6Path, output7Path, output8Path, output9Path, output10Path ]


  # --------------------------------------------------------------------------------------------
  # Merging of exposures
  
  if TEST_MODE_ON:
    # Disable merge, since it can take a while
    os.system(f"mv {output1Path} /tmp")
    os.system(f"rm {sessionData.path_temp}/*.hdr")
    os.system(f"mv {output1Path} {sessionData.sessionData.path_temp}/")
  
  # Not testing
  else:
    # Clear temp directory
    try:
      # Loop through each intermediate output file path and remove it
      for intermediateImage in intermediateOutputFilePaths:
          os.remove( f"{intermediateImage}" )

          curCmd = f"os.remove( {intermediateImage} )"

    except FileNotFoundError:
      pass
    except OSError as e:
      print(f"Error on command: {curCmd}")
      
      recordLog( sessionTime, "ERROR", e )
    finally:
      pass

    # Merge exposures
    try:
      os.system(f"hdrgen {' '.join(sessionData.paths_ldr)} -o {output1Path}"
                f" -r {sessionData.path_rsp_fn} -a -e -f -g")
    except Exception as e:
      recordLog( sessionTime, "ERROR", e )

  radiance_pipeline_percent = 10

  # --------------------------------------------------------------------------------------------



  # --------------------------------------------------------------------------------------------
  # Nullifcation of exposure value
  os.system(f"ra_xyze -r -o {output1Path} > {output2Path}")

  
  radiance_pipeline_percent = 20

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # Cropping and resizing
  os.system(f"pcompos -x {sessionData.diameter} -y {sessionData.diameter} {output2Path} "
            f"-{sessionData.crop_x_left} -{sessionData.crop_y_down}, > {output3Path}")

  
  radiance_pipeline_percent = 30

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # Vignetting correction
  os.system(f"pcomb -f {sessionData.path_vignetting} {output3Path} > {output4Path}")

  
  radiance_pipeline_percent = 40
  
  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # Crop             
  os.system(f"pfilt -1 -x {sessionData.target_x_resolution} -y {sessionData.target_y_resolution} "
            f"{output4Path} > {output5Path}")

  
  radiance_pipeline_percent = 50

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # Projection adjustment
  os.system(f"pcomb -f {sessionData.path_fisheye} {output5Path} > {output6Path}")

  
  radiance_pipeline_percent = 60

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # ND Filter correction
  os.system(f"pcomb -f {sessionData.path_ndfilter} {output6Path} > {output7Path}")

  
  radiance_pipeline_percent = 70

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # Photometric adjustment
  os.system(f"pcomb -h -f {sessionData.path_calfact} {output7Path} > {output8Path}")

  
  radiance_pipeline_percent = 80

  # --------------------------------------------------------------------------------------------


  # --------------------------------------------------------------------------------------------
  # HDR image header editing
  # Projection type
  if (osName == 'nt'):
    os.system( f"(get-content < {output8Path} "
                "| %{$_ -replace \"View\", \"d\" } && getinfo - < "
               f"{output8Path} > {output9Path}" )
    
  elif (osName == 'posix'):
    os.system(f"(getinfo < {output8Path} | sed \"/VIEW/d\" && getinfo - < {output8Path}) "
              f"> {output9Path}")

  # Real Viewing Angle
  os.system(f"getinfo -a \"VIEW = -vta -view_angle_vertical {sessionData.view_angle_vertical} "
            f"-view_angle_horizontal {sessionData.view_angle_horizontal}\" "
            f"< {output9Path} > {output10Path}")
  
  
  radiance_pipeline_percent = 90 
  
  # --------------------------------------------------------------------------------------------

  
  # --------------------------------------------------------------------------------------------
  # Validity check
  os.system(f"evalglare -V {output10Path}")

  
  radiance_pipeline_percent = 100

  # --------------------------------------------------------------------------------------------
