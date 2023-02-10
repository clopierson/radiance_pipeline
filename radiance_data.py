class RadianceData:
  def __init__(self, 
          diameter,
          xleft,
          ydown,
          vv,
          vh,
          targetx,
          targety,
          paths_ldr,
          path_temp,
          path_rsp_fn,
          path_fisheye,
          path_ndfilter,
          path_photometric):
            self.diameter         = diameter
            self.xleft            = xleft
            self.ydown            = ydown
            self.vv               = vv
            self.vh               = targetx
            self.targety          = targety
            self.paths_ldr        = paths_ldr
            self.path_temp        = path_temp
            self.path_rsp_fn      = path_rsp_fn
            self.path_fisheye     = path_fisheye
            self.path_ndfilter    = path_ndfilter
            self.path_photometric = path_photometric
            return

