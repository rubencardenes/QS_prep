# OpenCV C++ Cheatsheet

Assumes `using namespace std; using namespace cv;` (fine for an interview, not for production).

```cpp
#include <opencv2/opencv.hpp>
#if CV_VERSION_MAJOR >= 5
#include <opencv2/geometry.hpp>   // OpenCV 5: contourArea, boundingRect, arcLength,
#endif                            // getRotationMatrix2D, findHomography, solvePnP...
```

```bash
g++ -std=c++17 -O2 main.cpp $(pkg-config --cflags --libs opencv4) -o app   # opencv5 on brew
```

---

## 1. Mat: create, types, copy

```cpp
Mat img(200, 200, CV_8UC3, Scalar(0,0,0));   // (rows=H, cols=W) — H first!
Mat z = Mat::zeros(h, w, CV_8UC1);
Mat f = Mat::ones(h, w, CV_32FC1);
Mat wrap(h, w, CV_8UC1, myBuffer);           // wraps external memory, NO copy, no ownership

Mat b = a;              // SHALLOW: shares the pixel buffer (refcounted)
Mat c = a.clone();      // DEEP copy
a.copyTo(dst);          // deep copy, reallocates dst if needed
a.copyTo(dst, mask);    // copy only where mask != 0

Mat roi = img(Rect(x,y,w,h));   // VIEW into img: writing to roi writes to img
roi.setTo(Scalar(255));         // ...so this paints img
Mat indep = img(rect).clone();  // detach if you need independence
```

Type encoding: `CV_<bits><U|S|F>C<channels>`

| Type | Meaning | Element |
|---|---|---|
| `CV_8UC1` | grayscale 0..255 | `uchar` |
| `CV_8UC3` | color BGR | `Vec3b` |
| `CV_16SC1` | signed, e.g. Sobel output | `short` |
| `CV_32SC1` | int, e.g. labels | `int` |
| `CV_32FC1` | float | `float` |

```cpp
img.rows img.cols          // ints, NOT containers  (no .size() on them)
img.size()                 // Size(width, height)   — note the order flip!
img.type() img.depth() img.channels() img.total() img.elemSize()
img.step                   // bytes per row (>= cols*elemSize if it's a ROI)
img.isContinuous()         // false for most ROIs -> can't use a single flat loop
img.empty()                // ALWAYS check after imread
img.convertTo(dst, CV_32F, 1/255.0);         // type + scale (alpha), optional beta
saturate_cast<uchar>(value);                 // rounds + clamps to 0..255
```

## 2. Pixel access and traversal

```cpp
img.at<uchar>(y, x)            // (row, col) — y first
img.at<Vec3b>(y, x) = Vec3b(0,0,230);        // B,G,R
img.at<Vec3b>(y, x)[2] = 255;                // red channel

// Preferred: row pointers (no bounds check, works on non-continuous ROIs)
Mat out(img.size(), CV_8UC1);
for (int y = 0; y < img.rows; ++y) {            // rows -> y
    const uchar* rowIn = img.ptr<uchar>(y);
    uchar* rowOut = out.ptr<uchar>(y);
    for (int x = 0; x < img.cols; ++x)          // cols -> x
        rowOut[x] = rowIn[x];
}

// Color version
const Vec3b* row = img.ptr<Vec3b>(y);
float lum = 0.114f*row[x][0] + 0.587f*row[x][1] + 0.299f*row[x][2];   // B,G,R

// Fastest single-pass, only if continuous
if (img.isContinuous()) { const uchar* p = img.ptr<uchar>(0); /* total() elems */ }

img.forEach<uchar>([](uchar& p, const int* pos){ p = 255 - p; });   // parallelized
```

`at<>()` vs `ptr<>()`: `at` does a bounds assert in debug and recomputes the row address every call; `ptr` hoists it. In a tight loop `ptr` is the answer, and saying so is the point of the exercise.

## 3. Arithmetic and stats

```cpp
add(a,b,dst); subtract(a,b,dst); multiply(a,b,dst); divide(a,b,dst);   // saturating
absdiff(a, b, dst);                       // |a-b|, classic frame differencing
addWeighted(a, 0.7, b, 0.3, 0.0, dst);    // blending / overlays
bitwise_and/or/xor/not(a, b, dst, mask);

countNonZero(mask);
minMaxLoc(src, &minVal, &maxVal, &minLoc, &maxLoc);
Scalar m = mean(img);  meanStdDev(img, mu, sigma);  Scalar s = sum(img);
double d = norm(a, b, NORM_INF);          // max abs difference — great for tests
normalize(src, dst, 0, 255, NORM_MINMAX, CV_8U);

split(bgr, chans); merge(chans, bgr);     // channel <-> planes
flip(src, dst, 0/*x-axis*/ | 1/*y*/ | -1/*both*/);
rotate(src, dst, ROTATE_90_CLOCKWISE);    // exact, no interpolation
transpose(src, dst);
hconcat(a, b, dst); vconcat(a, b, dst);
copyMakeBorder(src, dst, top, bot, left, right, BORDER_CONSTANT, Scalar::all(114));
```

## 4. Color spaces and thresholding

```cpp
cvtColor(src, dst, COLOR_BGR2GRAY);       // COLOR_*, not IMAGE_*
cvtColor(src, dst, COLOR_BGR2HSV);        // H:0..179  S:0..255  V:0..255
cvtColor(src, dst, COLOR_BGR2RGB);        // needed before feeding most DNNs

inRange(hsv, Scalar(0,80,50), Scalar(10,255,255), mask);   // color segmentation
// RED wraps around: two ranges + bitwise_or (H≈0-10 and H≈170-179)

threshold(src, dst, 127, 255, THRESH_BINARY);       // _INV, _TRUNC, _TOZERO
double t = threshold(src, dst, 0, 255, THRESH_BINARY | THRESH_OTSU);  // returns the threshold
adaptiveThreshold(src, dst, 255, ADAPTIVE_THRESH_GAUSSIAN_C, THRESH_BINARY, 11, 2);
```

## 5. Filters and edges

```cpp
blur(src, dst, Size(3,3));                       // box
GaussianBlur(src, dst, Size(5,5), 1.5);          // ksize must be ODD
medianBlur(src, dst, 5);                         // best for salt & pepper
bilateralFilter(src, dst, 9, 75, 75);            // edge-preserving, slow

filter2D(src, dst, -1, kernel);                  // arbitrary kernel (correlation!)
                                                 // true convolution = flip the kernel

Sobel(src, gx, CV_16S, 1, 0, 3);                 // dx=1 -> vertical edges
Sobel(src, gy, CV_16S, 0, 1, 3);                 // NEVER output to CV_8U: negatives clip
convertScaleAbs(gx, gx8);                        // back to displayable 8U
magnitude(gxF, gyF, mag);                        // on CV_32F
Laplacian(src, dst, CV_16S, 3);

Canny(gray, edges, 50, 150);                     // blur first; ratio low:high ≈ 1:2..1:3
```

`BORDER_REFLECT_101` is the default border mode; alternatives `BORDER_REPLICATE` (= clamp), `BORDER_CONSTANT`.

## 6. Morphology

```cpp
Mat k = getStructuringElement(MORPH_RECT, Size(3,3));    // MORPH_ELLIPSE, MORPH_CROSS
erode(mask, dst, k, Point(-1,-1), 2);                    // 2 iterations
dilate(mask, dst, k);
morphologyEx(mask, dst, MORPH_OPEN,  k);   // erode+dilate: removes specks
morphologyEx(mask, dst, MORPH_CLOSE, k);   // dilate+erode: fills holes
morphologyEx(mask, dst, MORPH_GRADIENT, k);// outline
```

## 7. Contours, shapes, blobs

```cpp
vector<vector<Point>> contours;
vector<Vec4i> hierarchy;
findContours(mask, contours, RETR_EXTERNAL, CHAIN_APPROX_SIMPLE);  // note the spelling
// RETR_EXTERNAL outer only | RETR_LIST all, flat | RETR_TREE full hierarchy
// CHAIN_APPROX_SIMPLE compresses straight runs (4 pts for a rectangle)

double a   = contourArea(c);              // POLYGON area: a 20x20 px square -> 361, not 400
double per = arcLength(c, true);          // closed = true
Rect box   = boundingRect(c);             // exact pixel box (20x20)
RotatedRect rr = minAreaRect(c);          // oriented box; rr.points(pts4), rr.angle
minEnclosingCircle(c, center, radius);
convexHull(c, hull);
bool inside = pointPolygonTest(c, pt, false) >= 0;

vector<Point> approx;                     // Ramer-Douglas-Peucker
approxPolyDP(c, approx, 0.02 * arcLength(c, true), true);   // 3=triangle, 4=quad, >6≈circle

Moments M = moments(c);                   // centroid
Point2f centroid(M.m10/M.m00, M.m01/M.m00);

drawContours(canvas, contours, -1, Scalar(0,255,0), 2);     // -1 = all

// Alternative to contours for labelling blobs (often faster and gives stats directly)
Mat labels, stats, centroids;
int n = connectedComponentsWithStats(mask, labels, stats, centroids, 8, CV_32S);
for (int i = 1; i < n; ++i) {             // 0 is the background
    int area = stats.at<int>(i, CC_STAT_AREA);
    Rect r(stats.at<int>(i, CC_STAT_LEFT),  stats.at<int>(i, CC_STAT_TOP),
           stats.at<int>(i, CC_STAT_WIDTH), stats.at<int>(i, CC_STAT_HEIGHT));
}
```

## 8. Geometric transforms

```cpp
resize(src, dst, Size(w,h));                       // absolute
resize(src, dst, Size(), 0.5, 0.5, INTER_AREA);    // by factor
// INTER_AREA when SHRINKING (anti-aliased), INTER_LINEAR when enlarging,
// INTER_NEAREST for label/mask images (must not invent new values)

Mat M = getRotationMatrix2D(center, angleDeg, scale);   // 2x3, CCW positive
warpAffine(src, dst, M, dst_size, INTER_LINEAR, BORDER_CONSTANT, Scalar::all(0));

Mat H = getPerspectiveTransform(src4, dst4);            // 3x3, exactly 4 point pairs
warpPerspective(src, dst, H, Size(w,h));

Mat A = estimateAffinePartial2D(p1, p2);                // similarity from N points (RANSAC)
remap(src, dst, mapX, mapY, INTER_LINEAR);              // arbitrary per-pixel mapping
perspectiveTransform(ptsIn, ptsOut, H);                 // apply H to POINTS, not pixels
```

Warping does **inverse mapping** (for each destination pixel it looks up the source), which is why the output has no holes.

## 9. Features, matching, homography

```cpp
Ptr<ORB> orb = ORB::create(1000);                  // free; SIFT also in main repo now
vector<KeyPoint> k1, k2; Mat d1, d2;
orb->detectAndCompute(img1, noArray(), k1, d1);    // descriptor = local appearance vector
orb->detectAndCompute(img2, noArray(), k2, d2);

BFMatcher matcher(NORM_HAMMING);                   // NORM_L2 for SIFT/float descriptors
vector<vector<DMatch>> knn;
matcher.knnMatch(d1, d2, knn, 2);
vector<DMatch> good;                               // Lowe's ratio test
for (auto& m : knn) if (m[0].distance < 0.75f * m[1].distance) good.push_back(m[0]);

Mat Hm = findHomography(pts1, pts2, RANSAC, 3.0);  // RANSAC rejects outliers
goodFeaturesToTrack(gray, corners, 200, 0.01, 10); // Shi-Tomasi
cornerHarris(gray, resp, 2, 3, 0.04);
```

## 10. Template matching and Hough

```cpp
matchTemplate(img, templ, result, TM_CCOEFF_NORMED);   // result is (W-w+1)x(H-h+1), CV_32F
minMaxLoc(result, &minV, &maxV, &minL, &maxL);         // maxL = top-left of best match
// For multiple detections: threshold the result map + NMS

HoughLinesP(edges, lines, 1, CV_PI/180, 50, 30, 10);   // vector<Vec4i> x1,y1,x2,y2
HoughCircles(gray, circles, HOUGH_GRADIENT, 1, 20, 100, 30, 5, 50);  // vector<Vec3f>
```

## 11. Camera geometry (drone/UAV relevant)

```cpp
Mat K = (Mat_<double>(3,3) << fx,0,cx, 0,fy,cy, 0,0,1);
Mat dist = (Mat_<double>(1,5) << k1,k2,p1,p2,k3);

undistort(src, dst, K, dist);                      // convenience, recomputes maps every call
initUndistortRectifyMap(K, dist, noArray(), K, size, CV_16SC2, m1, m2);  // do this ONCE
remap(src, dst, m1, m2, INTER_LINEAR);             // ...then this per frame (much faster)

solvePnP(objectPts3D, imagePts2D, K, dist, rvec, tvec);      // pose from known geometry
solvePnPRansac(...);                               // with outliers
Rodrigues(rvec, R);                                // rotation vector <-> 3x3 matrix
projectPoints(objectPts3D, rvec, tvec, K, dist, imagePts);
calibrateCamera(objPts, imgPts, size, K, dist, rvecs, tvecs);
```

## 12. Video I/O, tracking, background

```cpp
VideoCapture cap(0);                       // or "file.mp4", or a GStreamer pipeline string
if (!cap.isOpened()) return -1;
cap.set(CAP_PROP_FRAME_WIDTH, 1280);
Mat frame; while (cap.read(frame)) { /* ... */ }   // cap >> frame also works

VideoWriter out("o.mp4", VideoWriter::fourcc('m','p','4','v'), 30, Size(w,h));
out.write(frame);

calcOpticalFlowPyrLK(prevGray, gray, p0, p1, status, err);   // sparse LK tracking
calcOpticalFlowFarneback(prevGray, gray, flow, 0.5,3,15,3,5,1.2,0);   // dense

Ptr<BackgroundSubtractorMOG2> bg = createBackgroundSubtractorMOG2();
bg->apply(frame, fgMask);

KalmanFilter kf(4, 2, 0);                  // constant-velocity tracker: [x,y,vx,vy]
kf.predict(); kf.correct(measurement);
```

## 13. DNN module

```cpp
Net net = dnn::readNet("model.onnx");                 // also Caffe/TF/Darknet
net.setPreferableBackend(DNN_BACKEND_CUDA);           // on Jetson: TensorRT beats this
net.setPreferableTarget(DNN_TARGET_CUDA_FP16);

Mat blob = dnn::blobFromImage(img, 1/255.0, Size(640,640), Scalar(),
                              /*swapRB=*/true, /*crop=*/false, CV_32F);  // NCHW float
net.setInput(blob);
Mat outp = net.forward();                             // or forward(outs, net.getUnconnectedOutLayersNames())

vector<int> keep;
dnn::NMSBoxes(boxes, scores, 0.25f, 0.45f, keep);     // built-in NMS
```

Say out loud: `blobFromImage` resizes **without** keeping aspect ratio unless you letterbox first; and on Jetson the production path is PyTorch → ONNX → **TensorRT** (FP16/INT8), not `cv::dnn`.

## 14. Drawing, I/O, debugging

```cpp
Mat img = imread("f.png", IMREAD_COLOR);   // BGR; IMREAD_GRAYSCALE, IMREAD_UNCHANGED
if (img.empty()) { cerr << "no image\n"; return -1; }
imwrite("out.png", img);
imshow("win", img); waitKey(0);            // NOTHING shows without waitKey

rectangle(img, Rect(10,10,20,20), Scalar(0,0,255), FILLED);   // or thickness=2
circle(img, center, r, color, 2);
line(img, p1, p2, color, 2, LINE_AA);
putText(img, "obj 0.93", Point(x,y-5), FONT_HERSHEY_SIMPLEX, 0.5, color, 1);
cout << M << endl;                         // Mat has operator<< (small matrices only)
```

## 15. Performance (the Jetson conversation)

```cpp
TickMeter tm; tm.start(); /* work */ tm.stop(); cout << tm.getTimeMilli() << " ms\n";
double t0 = getTickCount(); ... (getTickCount()-t0)/getTickFrequency();

setNumThreads(4);                          // OpenCV parallelizes internally by default
parallel_for_(Range(0, rows), [&](const Range& r){ /* rows r.start..r.end */ });

UMat u; img.copyTo(u);                     // T-API: same calls run on OpenCL if available
cuda::GpuMat g; g.upload(img); cuda::resize(g, g2, size); g2.download(out);
```

Rules of thumb: pass `const Mat&`, never by value in hot paths (cheap anyway — it's refcounted, but be explicit); preallocate destinations and reuse them across frames; do one `convertTo` instead of converting inside a loop; prefer ROIs over crops; CPU↔GPU transfers usually dominate, so batch them or use unified/zero-copy memory.

## 16. Gotchas that cost you the interview

- **BGR, not RGB.** `Scalar(0,0,255)` is red. DNNs almost always want RGB → `swapRB`.
- **Order flips everywhere**: `Mat(rows=h, cols=w)`, `at(y,x)`, but `Point(x,y)`, `Size(w,h)`, `Rect(x,y,w,h)`, `img.size()` = `Size(w,h)`.
- **`rows`/`cols` are ints**, not containers — no `.size()` on them; `img.size()` is the whole `Size`.
- **`Mat b = a;` is a shallow copy** and a ROI is a live view. Mutating either mutates the original.
- **uint8 overflows**: accumulate in `int`/`float`, write back with `saturate_cast<uchar>`.
- **Hue is 0..179** in OpenCV; red wraps and needs two `inRange` calls.
- **`contourArea` ≠ `countNonZero`**: polygon area vs pixel count.
- **Odd kernel sizes** for `GaussianBlur`/`medianBlur`.
- **Sobel into `CV_8U` loses all negative gradients** — use `CV_16S`/`CV_32F`.
- **Always check `imread` with `.empty()`** — it returns an empty Mat, it does not throw.
- **`imshow` needs `waitKey`**; float images are expected in 0..1.
- **OpenCV 5** moved `contourArea`, `boundingRect`, `arcLength`, `getRotationMatrix2D`,
  `getPerspectiveTransform`, `findHomography`, `solvePnP` to `opencv2/geometry.hpp`.

## 17. Snippets worth memorizing

```cpp
// IoU with cv::Rect — the & operator is the intersection
float iou(const Rect& a, const Rect& b) {
    float inter = (a & b).area();
    return inter / (a.area() + b.area() - inter);      // guard the 0 denominator
}
Rect safe = roi & Rect(0, 0, img.cols, img.rows);      // clip a ROI to the image
bool in   = rect.contains(pt);
Point tl  = rect.tl(), br = rect.br();

// Largest contour, cheap version (one contourArea call per contour)
vector<double> areas(contours.size());
transform(contours.begin(), contours.end(), areas.begin(),
          [](const vector<Point>& c){ return contourArea(c); });
size_t best = max_element(areas.begin(), areas.end()) - areas.begin();

// Letterbox resize (YOLO-style preprocessing)
double s = min(tw / (double)src.cols, th / (double)src.rows);
resize(src, r, Size(lround(src.cols*s), lround(src.rows*s)), 0, 0,
       s < 1 ? INTER_AREA : INTER_LINEAR);
copyMakeBorder(r, out, (th-r.rows)/2, th-r.rows-(th-r.rows)/2,
                       (tw-r.cols)/2, tw-r.cols-(tw-r.cols)/2,
               BORDER_CONSTANT, Scalar::all(114));

// Manual 3x3 convolution with clamped borders (the classic whiteboard exercise)
auto cl = [](int v, int lo, int hi){ return max(lo, min(v, hi)); };
int acc = 0;
for (int dy = -1; dy <= 1; ++dy)
  for (int dx = -1; dx <= 1; ++dx)
    acc += K[dy+1][dx+1] * img.at<uchar>(cl(y+dy,0,H-1), cl(x+dx,0,W-1));
out.at<uchar>(y,x) = saturate_cast<uchar>(acc);
```
