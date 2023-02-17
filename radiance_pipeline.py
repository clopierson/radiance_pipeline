import os
rp = __import__(__name__)
from radiance_data import RadianceData


def hdrgen(path_to_images, path_to_camera):
# in    path_to_images    string with <location to images>/*.JPG
#       path_to_camera    string with <location to camera>/camera.rsp
# out   creates file output1.hdr
  return ("hdrgen {} -o ../Intermediate/output1.hdr -r {} -a -e -f -g"
            .format(path_to_images, path_to_camera))

def pcompos(x, y, xleft, ydown, step):
  return ("pcompos -x {x} -y {y} ../Intermediate/output{pstep}.hdr -{xleft} -{ydown} > \
  ../Intermediate/output{step}.hdr".format(x=x, y=y, xleft=xleft, ydown=ydown, 
                                        pstep = step - 1, step = step))

def pfilt(xdim, ydim, step):
  return ("pfilt -1 -x {} -y {} ../Intermediate/output{}.hdr > ../Intermediate/output{}.hdr"
            .format(xdim, ydim, step - 1, step))

def pcomb(cal_file, step):
  return ("pcomb -f {} ../Intermediate/output{}.hdr > ../Intermediate/output{}.hdr"
          .format(cal_file, step - 1, step))

def radiance_pipeline(rd):

  diameter         = rd.diameter
  xleft            = rd.xleft
  ydown            = rd.ydown
  vv               = rd.vv
  vh               = rd.vh
  targetx          = rd.targetx
  targety          = rd.targety
  paths_ldr        = rd.paths_ldr
  path_temp        = rd.path_temp
  path_rsp_fn      = rd.path_rsp_fn
  path_vignetting  = rd.path_vignetting
  path_fisheye     = rd.path_fisheye
  path_ndfilter    = rd.path_ndfilter
  path_calfact     = rd.path_calfact


  test_mode = False

  if test_mode:
    os.system("mv ../Intermediate/output1.hdr /tmp")
    os.system("rm ../Intermediate/*")
    os.system("mv /tmp/output1.hdr ../Intermediate/")
  else:
    os.system("rm ../Intermediate/*")

    # Merging of exposures 
    os.system(hdrgen(" ".join(paths_ldr), 
                     path_rsp_fn))

  # Nullifcation of exposure value
  os.system("ra_xyze -r -o ../Intermediate/output1.hdr > ../Intermediate/output2.hdr")


  # Cropping and resizing
  os.system(pcompos(diameter, diameter, xleft, ydown, 3))

  # Vignetting correction
  os.system(pcomb("../Inputs/Parameters/vignetting_f5d6.cal", 4))

  # Crop
  os.system(pfilt(targetx, targety, 5))

  # Projection adjustment
  os.system(pcomb("../Inputs/Parameters/fisheye_corr.cal", 6))


  # ND Filter correction
  os.system(pcomb("../Inputs/Parameters/NDfilter_no_transform.cal", 7))

  # Photometric adjustment
  # os.system(pcomb("../Inputs/Parameters/CF_f5d6.cal", 8))
  os.system("pcomb -h -f ../Inputs/Parameters/CF_f5d6.cal ../Intermediate/output7.hdr > ../Intermediate/output8.hdr")

  # HDR image header editing
  header_step = 9
  os.system("(getinfo < ../Intermediate/output{pstep}.hdr  \
             | sed \"/VIEW/d\" && getinfo - < ../Intermediate/output{pstep}.hdr) \
             > ../Intermediate/output{step}.hdr"
             .format(pstep=header_step - 1, step=header_step))

  os.system("getinfo -a \"VIEW = -vta -vv {vv} -vh {vh}\" \
             < ../Intermediate/output{pstep}.hdr > \
             ../Intermediate/output{step}.hdr"
             .format(vv=vv, vh=vh, pstep=header_step, step=header_step+1))
  
  # Validity check
  os.system("evalglare -V ../Intermediate/output10.hdr")


def main():
  rd = RadianceData(
  diameter = 3612,
  xleft = 1019,
  ydown = 74,
  vv = 186,
  vh = 186,
  targetx = 1000,
  targety = 1000,
  paths_ldr = ["../Inputs/LDRImages/*.JPG"],
  path_temp = "../Intermediate/",
  path_rsp_fn = "../Inputs/Parameters/Response_function.rsp",
  path_vignetting = "",
  path_fisheye = "",
  path_ndfilter = "",
  path_calfact = ""
  )

  radiance_pipeline(rd)
  

if __name__ == "__main__":
  main()
