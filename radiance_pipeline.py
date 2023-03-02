import os
rp = __import__(__name__)
from radiance_pipeline.radiance_data import RadianceData
import sys

radiance_pipeline_percent = 0

def radiance_pipeline(rd):
  global radiance_pipeline_percent
  test_mode = False

  # Rerout errors to log file
  if rd.path_err != "":
    sys.stderr = open(rd.path_err, 'w')
  # Rereout other output to log file
  if rd.path_log != "":
    sys.stdout = open(rd.path_log, 'w')

  radiance_pipeline_percent = 0
  if test_mode:
    # Disable merge, since it can take a while
    os.system(f"mv {rd.path_temp}/output1.hdr /tmp")
    os.system(f"rm {rd.path_temp}/*.hdr")
    os.system(f"mv /tmp/output1.hdr {rd.rd.path_temp}/")
  
  # Not testing
  else:
    # Clear temp
    os.system(f"rm {rd.path_temp}/*.hdr")

    # Merging of exposures 
    os.system(f"hdrgen {' '.join(rd.paths_ldr)} -o {rd.path_temp}/output1.hdr"
              f" -r {rd.path_rsp_fn} -a -e -f -g")

  radiance_pipeline_percent = 10

  # Nullifcation of exposure value
  os.system(f"ra_xyze -r -o {rd.path_temp}/output1.hdr > {rd.path_temp}/output2.hdr")

  radiance_pipeline_percent = 20

  # Cropping and resizing
  os.system(f"pcompos -x {rd.diameter} -y {rd.diameter} {rd.path_temp}/output2.hdr "
            f"-{rd.crop_x_left} -{rd.crop_y_down}, > {rd.path_temp}/output3.hdr")

  radiance_pipeline_percent = 30

  # Vignetting correction
  os.system(f"pcomb -f {rd.path_vignetting} {rd.path_temp}/output3.hdr > "
            f"{rd.path_temp}/output4.hdr")

  radiance_pipeline_percent = 40
  
  # Crop
  os.system(f"pfilt -1 -x {rd.target_x_resolution} -y {rd.target_y_resolution} "
            f"{rd.path_temp}/output4.hdr "
            f"> {rd.path_temp}/output5.hdr")

  radiance_pipeline_percent = 50

  # Projection adjustment
  os.system(f"pcomb -f {rd.path_fisheye} {rd.path_temp}/output5.hdr > "
            f"{rd.path_temp}/output6.hdr")


  radiance_pipeline_percent = 60

  # ND Filter correction
  os.system(f"pcomb -f {rd.path_ndfilter} {rd.path_temp}/output6.hdr > "
            f"{rd.path_temp}/output7.hdr")


  radiance_pipeline_percent = 70

  # Photometric adjustment
  os.system(f"pcomb -h -f {rd.path_calfact} {rd.path_temp}/output7.hdr > {rd.path_temp}"
             "/output8.hdr")

  radiance_pipeline_percent = 80

  # HDR image header editing
  os.system(f"(getinfo < {rd.path_temp}/output8.hdr"
            f"| sed \"/VIEW/d\" && getinfo - < {rd.path_temp}/output8.hdr)"
            f" > {rd.path_temp}/output9.hdr")

  radiance_pipeline_percent = 90 

  os.system(f"getinfo -a \"VIEW = -vta -view_angle_vertical {rd.view_angle_vertical} "
            f"-view_angle_horizontal {rd.view_angle_horizontal}\" "
            f"< {rd.path_temp}/output9.hdr > "
            f"{rd.path_temp}/output10.hdr")
  
  # Validity check
  os.system(f"evalglare -V {rd.path_temp}/output10.hdr")

  radiance_pipeline_percent = 100

