# MLMouseBrain
A tool for identifying the functional regions of the medullary reticular formation in a developing brain using mouse brain data from the Allen Developing Mouse Brain Atlas (ADMBA).

## Research Paper (thanks to this project):
- https://ieeexplore.ieee.org/document/11621652/

## Features
- Downloading ISH images from the ADMBA (Normal/Binarized Images).
- Gridding Images at a specific resolution.
- Interacting with the [Image-to-Image ADMBA Synchronization API](https://brain-map.org/support/tutorials/image-to-image-synchronization) to perform Image-To-Reference and Reference-To-Image conversions.
- Mapping voxels across the P56 and P4 mouse brains.
- Binning voxels mapped to ISH images.
- Dilating mapped voxels.
- KNN-imputation for missing gene expression data
- Z-score normalization to normalize sagittal brain cross-section images
- Multi-threading for processing large volumes of mouse brain voxels and gene expression.
- Projected Cluster Proximity.

## Visualization and K-means clustering
- Use data in tandem with Brandon Kong's [orofacial atlas visualization tool](https://github.com/brandondkong/orofacial-atlas)

## Steps to use
 - Create a virtual environment and install all the dependencies in requirements.txt
 - Please stick to files marked with "new<filename>" as they are the refactored versions of old files.
 - Use classes and methods in main.py in the root directory.
 - Input your own CSV file of voxels with gene expression measurements.

## IMPORTANT!
- I am currently working on a High Performance C++20 rewrite for this project.
- Feel free to open issues, fork, or submit PR's!
