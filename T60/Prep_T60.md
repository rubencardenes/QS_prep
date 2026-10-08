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
- Interpolation with Zernike moments. More suitable for step edges (transitions between two flat regions). Zernike moments form an orthogonal basis therefore noise in high order components does not couple into low order moments used to compute the solution. 
- Parabolic fitting. Simply fitting a parabola with 3 pixel values located around the maximum. It is fast and simple but suffers from pixel locking and does not take into account the PSF. 
- Log-Gaussian fitting. We model the image intensity with a 2D gaussian PSF. Taking the log, reduces it to a parabolic fitting. It is in general more accurate then the method before, but still is not great.
- cv::CornerSubPix: implemented in opencCV. Used to refine corner detection. The idea es that in corners the gradients of each point are perpendicular to the line joiining it to the theoretical corner. Using this idea in a local window we can optimze solving a liner system iteratively.   
- cv::find4QuadCornerSubpix: Specialized for chessboard calibration targets. Fits two sets of intersecting lines across the dark/light quadrants of a checkerboard square to locate the saddle point with sub-pixel precision.
- cv::simpleBlobDetector: Uses CoG method (iterative spatial moments for subpixel precision). It uses multiple thresholds to find binary masks and apply the moments for all of them. Computationally inefficient. 

# Co-registration 
- Cross-correlation methods matchTemplate
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

For calibration in the nanometer scale we need to use quartz with chorme-on-glass litography patterns, using circular dot arrays. Quartz has very low thermal expansion. 

# Implementation details 
Once camera is calibrated:
 Instead of applying a transformation that converts all the pixel coordinates, x,y into World coordinates, Xw,Yw,Zw, we rather apply the transformation from the sub-pixel coordinates of the fiducials or points we want to measure to the world coordinates, which is a lot more efficient.
 - Dense Image Warping, requires remapping, too expensive for this application
 - Sparse Point Transformation: 

# Industrial cameras
- Global shutter
- Monochrome camera
- Camera Interface: 
   - MIPI CSI 2: 1.5-2.5 Gbps direct embeded bus available in Jetsons 
   - 10GigE Vision: low latenciy 
   - CoaxPress: Up to 12.5 Gbps, ultra-low latency 

# Computing and frame grabber
FPGA: deterministic acquisition

# Interferometry
Requires expensive a setups and look only at simple points. 
Sensitive to air turbulences. 
Extremely precise. 

# OpenCV
## Feature detection methods
- cornerHarris: Computes the second moment autocorrelation matric (structure tensor) and decides if a feature is good if det(M)-k * trace(M)^2 (the simplest thing you can do)
goodfeaturestoTrack: Shi-Tomasi method. Directly computes the eigenvalues of M. Uses a different response R=min(lambda1, lambda2)
fastFeatureDetector: extremely fast method. Features from Accelerated Segment Test. Examina un circula de pixeles alrededor de un pto candidato y lo fija si hay mucho pontos consecutivos que son mas claros o oscuros que el centro. En ORB se usa este method combinado con otras mejoras. 
simpleBlobDetector: uses CoG method in multiple binarizations of the image. 
- SIFT: Scale Invariant Feature Transform. Computes Difference of Gaussians scale-spacem, and then use gradient histograms as descriptors 
- ORB: It uses Hamming distance which is faster than SIFT 
- AKAZE
- BRISK: FAST in sacel-space pyramid
- MSER 

# Questions
What is the target FPS and latency that you want to achieve?
Is the hardware setup already decided? 
Is there any plans to use advance 
What are the targets that you want to identify in the image? 
How are you dealing with camera calibration? 
What algorithms do you have in mind? 
