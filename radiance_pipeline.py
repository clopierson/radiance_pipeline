import os
import sys 
import platform
from pathlib import Path
import time
from dataclasses import dataclass


from submodules.radiance_pipeline.radiance_data import RadianceData
from submodules.radiance_pipeline.logs import *


# Apply different merging logic
TEST_MODE_ON = False

@dataclass
class PipelineStage:
  cmd: str
  altcmd: str
  percent_difference: int
  status_text: str
  finishmsg: str
  skip: bool = False

rp = __import__(__name__)

def radiance_pipeline_get_percent():
  return radiance_pipeline_percent

def radiance_pipeline_get_status_text():
  return radiance_pipeline_status_text

def radiance_pipeline_get_finished():
  return radiance_pipeline_finished

def radiance_pipeline( sessionData ):
  global radiance_pipeline_percent
  global radiance_pipeline_status_text
  global radiance_pipeline_finished
  radiance_pipeline_finished = False
  radiance_pipeline_percent = 0
  radiance_pipeline_status_text = "Setting up..."

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
  intermediateOutputFilePaths = [ output1Path, output2Path, output3Path, output4Path, 
                                 output5Path, output6Path, output7Path, output8Path, 
                                 output9Path, output10Path ]

  # --------------------------------------------------------------------------------------------
  # Merging of exposures
  radiance_pipeline_status_text = "Merging exposures (may take a while)"
  if TEST_MODE_ON:
    # Disable merge, since it can take a while
    os.system(f"mv {output1Path} /tmp")
    os.system(f"rm {sessionData.path_temp}/*.hdr")
    os.system(f"mv {output1Path} {sessionData.path_temp}/")
  
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
      radiance_pipeline_percent = 5
      if sessionData.path_rsp_fn is not None:
        os.system(f"hdrgen {' '.join(sessionData.paths_ldr)} -o {output1Path}"
                  f" -r {sessionData.path_rsp_fn} -a -e -f -g")
      else:
        os.system(f"hdrgen {' '.join(sessionData.paths_ldr)} -o {output1Path}"
                  f" -a -e -f -g")
        
    except Exception as e:
      recordLog( sessionTime, "ERROR", e )
    finally:
      print("Finished merging exposures.")
      radiance_pipeline_percent = 10

  # --------------------------------------------------------------------------------------------

  pipeline = [
  PipelineStage(f"ra_xyze -r -o {output1Path} > {output2Path}", None, 10, 
  "Nullifying exposures", "Finished nullifying exposures"),

  PipelineStage(f"pcompos -x {sessionData.diameter} -y {sessionData.diameter} {output2Path} "
  f"-{sessionData.crop_x_left} -{sessionData.crop_y_down}, > {output3Path}", None, 10,
  "Cropping", "Finished cropping"),

  PipelineStage(f"pcomb -f {sessionData.path_vignetting} {output3Path} > {output4Path}", 
                f"cp {output3Path} {output4Path}", 10, "Correcting vignetting", 
                "Finished correcting vignetting", sessionData.path_vignetting is None),

  PipelineStage(f"pfilt -1 -x {sessionData.target_x_resolution} -y {sessionData.target_y_resolution} "
  f"{output4Path} > {output5Path}", None, 10, "Resizing", "Finished resizing"),

  PipelineStage(f"pcomb -f {sessionData.path_fisheye} {output5Path} > {output6Path}", 
  f"cp {output5Path} {output6Path}", 10, "Adjusting fisheye", "Finished adjusting fisheye",
  sessionData.path_fisheye is None),

  PipelineStage(f"pcomb -f {sessionData.path_ndfilter} {output6Path} > {output7Path}",
  f"cp {output6Path} {output7Path}", 10, "Correcting neutral density filter",
  "Finished correcting neutral density filter",
  sessionData.path_ndfilter is None),

  PipelineStage(f"pcomb -h -f {sessionData.path_calfact} {output7Path} > {output8Path}",
  f"cp {output7Path} {output8Path}", 10, "Performing photometric adjustment", 
  "Finished photometric adjustment",
  sessionData.path_calfact is None),
  
  PipelineStage(f"(getinfo < {output8Path} | sed \"/VIEW/d\" && getinfo - < {output8Path}) "
          f"> {output9Path}", None, 5, "Editing header", "Finished editing image header"),

  PipelineStage(f"getinfo -a \"VIEW = -vta -view_angle_vertical {sessionData.view_angle_vertical} "
          f"-view_angle_horizontal {sessionData.view_angle_horizontal}\" "
          f"< {output9Path} > {output10Path}", None, 5, "Adjusting for real viewing angle",
          "Finished adjusting for real view angle"),

  PipelineStage(f"evalglare -V {output10Path}", None, 10, "Performing validity check",
  "Finished output image validity check")
  ]

  for stage in pipeline:
    radiance_pipeline_status_text = stage.status_text
    try:
      if not stage.skip:
        os.system(stage.cmd)
      else:
        os.system(stage.altcmd)
    except Exception as e:
      recordLog(sessionTime, "ERROR", e)
      print(f"Radiance pipeline error: {e}")
    finally:
      print(stage.finishmsg)
      radiance_pipeline_percent += stage.percent_difference

  radiance_pipeline_status_text = "Finished"
  radiance_pipeline_finished = True
