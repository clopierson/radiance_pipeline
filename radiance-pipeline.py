import os

################################################################################


def hdrgen(path_to_images, path_to_camera):
# in    path_to_images    string with <location to images>/*.JPG
#       path_to_camera    string with <location to camera>/camera.rsp
# out   creates file output1.hdr
  return ("hdrgen {} -o Intermediate/output1.hdr -r {} -a -e -f -g"
            .format(path_to_images, path_to_camera))

def pcompos(x, y, xleft, ydown, step):
  return ("pcompos -x {x} -y {y} Intermediate/output{pstep}.hdr -{xleft} -{ydown} > \
  Intermediate/output{step}.hdr".format(x=x, y=y, xleft=xleft, ydown=ydown, 
                                        pstep = step - 1, step = step))

def pfilt(xdim, ydim, step):
  return ("pfilt -1 -x {} -y {} Intermediate/output{}.hdr > Intermediate/output{}.hdr"
            .format(xdim, ydim, step - 1, step))

def pcomb(cal_file, step):
  return ("pcomb -f {} Intermediate/output{}.hdr > Intermediate/output{}.hdr"
          .format(cal_file, step - 1, step))

def radiance_pipeline(xres, yres, diameter, xleft, ydown, vv, vh, targetx, targety): 
  test_mode = True

  if test_mode:
    os.system("mv Intermediate/output1.hdr /tmp")
    os.system("rm Intermediate/*")
    os.system("mv /tmp/output1.hdr Intermediate/")
  else:
    os.system("rm Intermediate/*")

    # Merging of exposures 
    os.system(hdrgen("Inputs/LDRImages/*.JPG", 
                     "Inputs/Parameters/Response_function.rsp"))

  # Nullifcation of exposure value
  os.system("ra_xyze -r -o Intermediate/output1.hdr > Intermediate/output2.hdr")

  # Cropping and resizing
  os.system(pcompos(diameter, diameter, xleft, ydown, 3))
  os.system(pfilt(xres, yres, 4))

  # Projection adjustment
  os.system(pcomb("Inputs/Parameters/fisheye_corr.cal", 5))

  # Vignetting correction
  os.system(pcomb("Inputs/Parameters/vignetting_f5d6.cal", 6))

  # ND Filter correction
  os.system(pcomb("Inputs/Parameters/NDfilter_no_transform.cal", 7))

  # Photometric adjustment
  os.system(pcomb("Inputs/Parameters/CF_f5d6.cal", 8))

  # HDR image header editing
  header_step = 9
  os.system("getinfo < Intermediate/output{pstep}.hdr  \
             | sed \"/VIEW/d\" && getinfo - < Intermediate/output{pstep}.hdr \
             > Intermediate/output{step}.hdr"
             .format(pstep=header_step - 1, step=header_step))

  os.system("getinfo -a \"VIEW = -vta -vv {vv} -vh {vh}\" \
             < Intermediate/output{pstep}.hdr > \
             Intermediate/output{step}.hdr"
             .format(vv=vv, vh=vh, pstep=header_step, step=header_step+1))
  
  # Validity check
  os.system("evalglare -V Intermediate/output10.hdr")


def main():
  xres = 5616
  yres = 3744
  diameter = 3612
  xleft = 1019
  ydown = 74
  vv = 186
  vh = 186
  targetx = 1000
  targety = 1000
  radiance_pipeline(xres, yres, diameter, xleft, ydown, vv, vh, targetx, targety)
  

if __name__ == "__main__":
  main()
