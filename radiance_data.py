from dataclasses import dataclass

@dataclass
class RadianceData:
    '''
    radiance_pipeline API.
    For params, see paper by Clotilde Pierson.

    cmd_merge := "hdrgen"
               | "raw2hdr"
               | None (Automatic pick based on extension in paths_ldr)
               TODO: add psftools to cmd_merge
    '''
    diameter: int
    crop_x_left: int
    crop_y_down: int
    view_angle_vertical: int
    view_angle_horizontal: int
    target_x_resolution: int
    target_y_resolution: int
    paths_ldr: [str]
    path_temp: str
    path_rsp_fn: str = None
    path_vignetting: str = None
    path_fisheye: str = None
    path_ndfilter: str = None
    path_calfact: str = None
    path_errors: str = None
    path_logs: str = None
    cmd_merge: str = None
