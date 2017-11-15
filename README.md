LabelV is a semi-automatic video annotation tool for computer vision training data generation

## Installation

    sudo apt install ffmpeg
    
    pip install .

### Note:
   Getting OpenCV video capture to work on an Ubuntu machine could be tricky. The pip installation never worked for me, so I ended up building both openCV-python and openCV-contrib-python from source. 

## Quick start.
   - clone this repository and from the root directory, install it and then run
   
    labelv -v sample_video.mp4

   - draw four bounding boxes for the leading points around your object (press return after drawing each box)
   - press SPACEBAR to get to choose a new object to track with/without a new label
     * press enter without a new label to use the previous label for the object
     * or enter the new label for the new object
   - press ESC to terminate the process
   - view the screen capture on _output.avi_

## Arguments
   * -v/--video: the input video you want to use for tracking/labeling task (default: video device)
   * -l/--label: label of the object you choose to track (default: 'label')
   * -fp/--frame path: path to the directory to save video frames in (default: Images/)
   * -lp/label path: path to the file to save frame labels in (default: labels/label.csv)
   * -m/--mode: mode to open the labels file in, a for append, w for write (default: w)
   * -fr/-frame rate: rate to save frames and labels at. Every 1/fr is saved (default: 1)
   * -fn/--file name: base name for each frame (imporant to set or frames from the previous videos will be replaced (default: frame)

## More detailed explanation and show-case

   [https://asadisaghar.github.io/video-labeler/](https://asadisaghar.github.io/video-labeler/)
