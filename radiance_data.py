from dataclasses import dataclass

@dataclass
class RadianceData:
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
