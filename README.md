# Radiance Pipeline

An submodule for producing calibrated HDR images from multiple LDR images with different exposure levels. For more information, see the [wiki](https://github.com/zimmermannliam/radiance_pipeline/wiki).

To read more about the process of generating an HDR image from LDR image input, see the research paper by Clotilde Pierson [here](https://doi.org/10.1080/15502724.2019.1684319).

### Build status

No issues

### Code style

PEP8, but with a tab = 2 spaces

### Tech used

This project uses radiance and HDRGen.

Radiance: https://www.radiance-online.org/

HDRGen: http://anyhere.com/

### Features

- Produces calibrated HDR files using correction for vignetting, fisheye, NDFilter, and photometric adjustment
- Meant to be used by the main [HDRI Calibration Tool](https://github.com/XiangyuLijoey/HDRICalibrationTool) application.

### Installation

See [wiki/install](https://github.com/zimmermannliam/radiance_pipeline/wiki/Install)

### Tests

See the unit testing repo [rp_test](https://github.com/zimmermannliam/rp_test/)

### How to use?

This is meant to be dropped in the folder:

`submodules.radiance_pipeline`

So import it with 

```
from submodules.radiance_pipeline.radiance_pipeline import radiance_pipeline
from submodules.radiance_pipeline.radiance_data import RadianceData
```

And then it can be run by creating a `radianceData` object and passing it to `radiance_pipeline()`.

It can be added as a thread, see an example [here](https://github.com/XiangyuLijoey/HDRICalibrationTool/blob/main/src/progress_window.py)

### Contribute

Simply fork it and pull request :) Add zimmermannliam as a reviewer.

### Credits

Nathaniel Klump, Liam Zimmermann, Xiangyu "Joey" Li, Clotilde Pierson.
