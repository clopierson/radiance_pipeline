from dataclasses import dataclass

@dataclass
class RadianceData:
    diameter: int = None
    crop_x_left: int = None
    crop_y_down: int = None
    view_angle_vertical: int = None
    view_angle_horizontal: int = None
    target_x_resolution: int = None
    target_y_resolution: int = None
    paths_ldr: [str] = None
    path_temp: str = None
    path_rsp_fn: str = None
    path_vignetting: str = None
    path_fisheye: str = None
    path_ndfilter: str = None
    path_calfact: str = None
    path_errors: str = None
    path_logs: str = None
