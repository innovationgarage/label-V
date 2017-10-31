LabelV is a semi-automatic video annotation tool for computer vision training data generation

## Dependencies
   - numpy
   - opencv-python
   - opencv-contrib-python

### Note:
    Getting OpenCV video capture to wotk on an Ubuntu machine could be tricky. The pip installation never worked for me, so I ended up building bth openCV-python and openCV-contrib-python from source. (Read about it) [https://asadisaghar.github.io/video-labeler/].

## Quick start.
   - clone this repository and from the root directory run
   ´´´
   python labelv.py -v sample_video.mp4
   ´´´
   or simply run
   ´´´
   python labelv.py
   ´´´
   to use your default video device (/dev/video0)

   - draw four bounding boxes for the leading points around your object (press return after drawing each box)
   - press SPACEBAR to get to choose a new object to track with/without a new label
     * press enter without a new label to use the previous label for the object
     * or enter the new label for the new object
   - press ESC to terminate the process
   - view the screen capture on output.avi

## Arguments
   * -v/--video: the input video you want to use for tracking/labeling task (default: video device)
   * -l/--label: label of the object you choose to track (default: 'label')
   * -fp/--frame path: path to the directory to save video frames in (default: Images/)
   * -lp/label path: path to the file to save frame labels in (default: labels/label.csv)
   * -m/--mode: mode to open the labels file in, a for append, w for write (default: w)
   * -fr/-frame rate: rate to save frames and labels at. Every 1/fr is saved (default: 1)
   * -fn/--file name: base name for each frame (imporant to set or frames from the previous videos will be replaced (default:'frame')
   * -o/--output: path to the output video (default: output.avi)

## More detailed explanation and show-case

   https://asadisaghar.github.io/video-labeler/
