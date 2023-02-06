import os

################################################################################


def hdrgen(path_to_images, path_to_camera):
# in    path_to_images    string with <location to images>/*.JPG
#       path_to_camera    string with <location to camera>/camera.rsp
# out   creates file output1.hdr
  os.system("hdrgen {} -o Intermediate/output1.hdr -r {} -a -e -f -g"
            .format(path_to_images, path_to_camera))

def main():
  os.system("rm Intermediate/*")
  hdrgen("Inputs/LDRImages/*.JPG", "Inputs/Parameters/Response_function.rsp")
  os.system("ra_xyze -r -o Intermediate/output1.hdr > Intermediate/output2.hdr")
  

if __name__ == "__main__":
  main()
