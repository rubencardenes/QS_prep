# Sub-pixel estimation
- CoG Image moments, method. Compute the CoG of a given window where the fiducial is located. 
    x_estimated = M10 / M00
    y_estimated = M01 / M00
    M10 ( M00 = Sum_x Sum_y x * I(x,y) / Sum_x Sum_y I(x,y) 
    - Needs background substraction to avoid the method biasing the result towerds the center of the window
    - Suffers from pixel locking
    - Power weighted moments. To suppress even more the background contributions using exponentiation of the signal contributes to improve the result concentrating the weights on high signal to noise ration pixels. Powers of 2 or 3 are used. Higher collapses into argmax. 
    - An iterative approach improves the accuracy
- Subpixel Edge detection (Steger Method). 
    - Computes the Hessian matrix using gaussian filters. 
    - Then using the eigenvector analysis, we can estimate the center of an edge with subpixel precision taking the eigenvector direction corresponding to the highest eigenvalue. 
    - Using a polinomial approach, with Taylor expansion approximation, we can get an accurate estimation of the center of a given edge.
    - It doesn't suffer from pixel locking.  
- Interpolation with Zernike moments. ???
- Parabolic fitting. Simply fitting a parabola with 3 pixel values located around the maximum. It is fast and simple but suffers from pixel locking and does not take into account the PSF. 
- Log-Gaussian fitting. We model the image intensity with a 2D gaussian PSF. Taking the log, reduces it to a parabolic fitting. It is in general more accurate then the method before, but still is not great.

# Co-registration 
- Cross-correlation methods 
- Cross-correlation in the freq space, with upsampling using matricial DFT. 
   Step 1. Find Offset in pixel precision
   - Compute the FFT of the two images.
   - Compute R(u, v) the cross-power spectrum 
   - Compute iFFT of that r(x,y) 
   - Find the peak of r(x,y) -> x0, y0 in integer precision
   Step 2. Subpixel refinement
   - Compute r_sub using the DFT in matricial form: r_sub = Ey * R * Ex, using kernels around x0, y0 upsampled by k=100. If we use 1.5x1.5 window and upsampling of 100, it means a final r_sub of 150x150. 
   - Final displacement in subpixel coordinates is xd,yd = argmax(r_sub) 
- Point-based coregistration Optical-Flow, SuperGlue 
- Transformer based using LoFTR (Local features with transformers)

# Camera calibration 
Intrinsic parameters: focal lenght (fx, fy), gamma, optical center (cx, cy)
     Radial distorsion parameters: k1, k2, k3
     Tangencial distorsion parameters: p1, p2

Extrinsic parameters: Rotation, translation 

- Telecentric cameras: ensure that chief rays remain mainly parallel in the object-space or the image space. Then magnification remains constant with changes of the object in the Z dimension (along the camera axis) 
- Bi-telecentric cameras: ensure that chief rays ramin mainly parallel in object space AND image space. These are bigger and more expensive. 

For calibration in the nanometer scale we need to use quartz with chorme-on-glass litography patterns, uainf circular dot arrays. Quartz has very low thermal expansion. 

# Implementation details 
Once camera is calibrated:
 Instead of applying a transformation that converts all the pixel coordinates, x,y into World coordinates, Xw,Yw,Zw, we rather apply the transformation from the sub-pixel coordinates of the fiducials or points we want to measure to the world coordinates, which is a lot more efficient.
 - Dense Image Warping, requires remapping, too expensive for this application
 - Sparse Point Transformation: 

# Industrial cameras
- Global shutter
- Interface: 
   - MIPI CSI 2: 1.5-2.5 Gbps direct embeded bus available in Jetsons 
   - 10GigE Vision: low latenciy 
   - CoaxPress: Up to 12.5 Gbps, ultra-low latency 
    