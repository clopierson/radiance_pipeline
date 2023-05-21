'''
Radiance pipeline: Main action for the creation of calibrated HDR 
images.
'''
import os
import platform
from pathlib import Path
from dataclasses import dataclass
# import time


from .radiance_data import RadianceData
# from submodules.radiance_pipeline.logs import recordLog


radiance_pipeline_percent: int
radiance_pipeline_status_text: str
radiance_pipeline_finished: bool
radiance_pipeline_cancelled: bool
radiance_pipeline_error: bool

@dataclass
class PipelineStage:
    '''
    Each command in the pipeline can take this format.
    '''
    cmd: str
    altcmd: str
    percent_difference: int
    status_text: str
    finish_text: str
    skip: bool = False

rp = __import__(__name__)

def radiance_pipeline_get_percent():
    '''
    Getter for the percent finsihed global. Use in threads.
    '''
    return radiance_pipeline_percent

def radiance_pipeline_get_status_text():
    '''
    Getter for the status text global. Use in threads.
    '''
    return radiance_pipeline_status_text

def radiance_pipeline_get_finished():
    '''
    Getter for the finished bool global. Use in threads.
    '''
    return radiance_pipeline_finished

def copy_cmd(os_name, src, dest):
    '''
    Get a string contianing the copy command based on the OS
    '''
    if os_name == "nt":
        return f"copy {src} {dest}"
    return f"cp {src} {dest}"

def vignetting_cmd(os_name, src, dest, session_data):
    '''
    Get a string containing the vignetting command, since windows does
    not like the -e flag
    '''
    if os_name == "nt":
        return f"pcomb -f {session_data.path_vignetting} {src} > {dest}"
    return (f"pcomb -f {session_data.path_vignetting} -e 'diameter={session_data.diameter}' "
            f"{src} > {dest}")

def clear_temp(output_path):
    '''
    Clear the temp directory of previous run's output files.
    '''
    cur_cmd = None
    try:
        # Loop through each intermediate output file path and remove it
        for output_img in output_path[1:]:
            cur_cmd = f"os.remove({output_img})"
            os.remove(f"{output_img}")
    except FileNotFoundError:
        pass
    except OSError as exc:
        print(f"Error on command: {cur_cmd}")
        print(f"ERROR: {exc}")
        # recordLog(session_time, "ERROR", e)
    finally:
        pass

def cancel_pipeline():
    '''
    Cancel pipeline in-between stages before it's fully finished. Use in thread.
    '''
    global radiance_pipeline_cancelled
    radiance_pipeline_cancelled = True

def radiance_pipeline(session_data: RadianceData):
    '''
    Main action for the module
    '''
    global radiance_pipeline_percent
    global radiance_pipeline_status_text
    global radiance_pipeline_finished
    global radiance_pipeline_cancelled
    global radiance_pipeline_error
    radiance_pipeline_finished = False
    radiance_pipeline_percent = 0
    radiance_pipeline_status_text = "Setting up..."
    radiance_pipeline_cancelled = False
    radiance_pipeline_error = False

    # Grab time pipeline session started for log filenames, only want 1 per session
    # session_time = time.strftime("%Y%m%d-%H%M%S")

    # Get OS Platform info
    os_name = os.name
    os_system = platform.system()
    os_release = platform.release()
    os_version = platform.version()

    print(f"OS Name: {os_name}")
    print(f"OS System: {os_system}")
    print(f"OS Release: {os_release}")
    print(f"OS Version: {os_version}")
    print("\n")

    # Ensure temp directory exists for storing intermediate output files from each pipeline step
    Path(session_data.path_temp).mkdir(mode=0o755, parents=True, exist_ok=True)

    # Joining paths for intermediate file results with absolute path of temp directory:
    # cross-platform filepaths
    output_path = [None]
    for i in range(1, 11):
        output_path.append(os.path.join(session_data.path_temp, f"output{i}.hdr"))

    # Clear temp directory
    clear_temp(output_path)

    pipeline = [
PipelineStage(cmd=f"hdrgen {' '.join(session_data.paths_ldr)} -o {output_path[1]}"
              f" -r {session_data.path_rsp_fn} -a -e -f -g",
              altcmd=f"hdrgen {' '.join(session_data.paths_ldr)} -o {output_path[1]}"
              f" -a -e -f -g",
              percent_difference = 5,
              status_text="Merging exposures (may take a while)",
              finish_text="Finished merging exposures",
              skip=session_data.path_rsp_fn is None),

PipelineStage(cmd= f"ra_xyze -r -o {output_path[1]} > {output_path[2]}",
              altcmd=None,
              percent_difference=10,
              status_text="Nullifying exposures",
              finish_text="Finished nullifying exposures",
              skip=False),

PipelineStage(cmd=f"pcompos -x {session_data.diameter} -y {session_data.diameter} "
                  f"{output_path[2]} -{session_data.crop_x_left} "
                  f"-{session_data.crop_y_down}, > {output_path[3]}",
              altcmd=None,
              percent_difference=10,
              status_text="Cropping",
              finish_text="Finished cropping",
              skip=False),

PipelineStage(cmd=vignetting_cmd(os_name, output_path[3], output_path[4], session_data),
              altcmd=copy_cmd(os_name, output_path[3], output_path[4]),
              percent_difference=10,
              status_text="Correcting vignetting",
              finish_text="Finished correcting vignetting",
              skip=session_data.path_vignetting is None),

PipelineStage(cmd=f"pfilt -1 -x {session_data.target_x_resolution} -y "
                  f"{session_data.target_y_resolution} {output_path[4]} > {output_path[5]}",
              altcmd=None,
              percent_difference=10,
              status_text="Resizing",
              finish_text="Finished resizing",
              skip=False),

PipelineStage(cmd=f"pcomb -f {session_data.path_fisheye} {output_path[5]} > {output_path[6]}",
              altcmd=copy_cmd(os_name, output_path[5], output_path[6]),
              percent_difference=10,
              status_text="Adjusting fisheye",
              finish_text="Finished adjusting fisheye",
              skip=session_data.path_fisheye is None),

PipelineStage(cmd=f"pcomb -f {session_data.path_ndfilter} {output_path[6]} > "
                  f"{output_path[7]}",
              altcmd=copy_cmd(os_name, output_path[6], output_path[7]),
              percent_difference=10,
              status_text="Correcting neutral density filter",
              finish_text="Finished correcting neutral density filter",
              skip=session_data.path_ndfilter is None),

PipelineStage(cmd=f"pcomb -h -f {session_data.path_calfact} {output_path[7]} > "
                  f"{output_path[8]}",
              altcmd=copy_cmd(os_name, output_path[7], output_path[8]),
              percent_difference=10,
              status_text="Performing photometric adjustment",
              finish_text="Finished photometric adjustment",
              skip=session_data.path_calfact is None),

PipelineStage(cmd=f"(getinfo < {output_path[8]} | sed \"/VIEW/d\" && getinfo - < "
                  f"{output_path[8]}) > {output_path[9]}",
              altcmd=None,
              percent_difference=5,
              status_text="Editing header",
              finish_text="Finished editing image header",
              skip=None),

PipelineStage(cmd=f"getinfo -a \"VIEW = -vta "
                  f"-view_angle_vertical {session_data.view_angle_vertical} "
                  f"-view_angle_horizontal {session_data.view_angle_horizontal}\" "
                  f"< {output_path[9]} > {output_path[10]}",
              altcmd=None,
              percent_difference=5,
              status_text="Adjusting for real viewing angle",
              finish_text="Finished adjusting for real view angle",
              skip=None),

PipelineStage(cmd=f"evalglare -V {output_path[10]}",
              altcmd=None,
              percent_difference=10,
              status_text="Performing validity check",
              finish_text="Finished output image validity check",
              skip=None)
    ]

    for stage in pipeline:
        # Check if pipeline got cancelled in between steps
        if radiance_pipeline_cancelled:
            print("Cancelling active pipeline...")
            break
        if radiance_pipeline_error:
            print("Error, cancelling active pipeline...")
            break

        radiance_pipeline_status_text = stage.status_text

        try:
            if not stage.skip:
                os.system(stage.cmd)
            else:
                os.system(stage.altcmd)
        except Exception as exc:
            radiance_pipeline_status_text = f"Error on \"{stage.status_text}\": {exc}"
            print(radiance_pipeline_status_text)
            radiance_pipeline_cancelled = True
        finally:
            print(stage.finish_text)
            radiance_pipeline_percent += stage.percent_difference

    # Set status text
    if radiance_pipeline_cancelled:
        radiance_pipeline_status_text = "Canceled"
    else:
        radiance_pipeline_status_text = "Finished"

    # Set finished flag
    radiance_pipeline_finished = True
