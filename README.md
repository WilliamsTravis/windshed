# windshed
Exploring ways to calculate viewsheds from a point on the ground to a wind turbine considering topography and other visual obstacles.

So far, I just have one benchmarking test (windshed/test.py) that comares an xarray-spatial viewshed routine with an SRTM tile and a US Wind Turbine Database Turbine. This is simply to show the difference between their CPU and GPU methods. To run, it requires an NVIDIA GPU, the CUDA Toolkit, and the requirements for this package. 
