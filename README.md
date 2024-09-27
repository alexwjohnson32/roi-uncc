# roi-uncc
Repository for students and researchers working on the ROI project at UNCC

# Docker Image with Project Toolsets

The various software tools required for this project are included in a docker image built by the [Dockerfile](docker/Dockerfile) given in roi-uncc/docker. This image is built by executing:

```bash
docker build -t roi-img .
```
in the directory Dockerfile exists in.

The image can be run using :

```bash
docker run --rm -v /ABSOLUTE/PATH/ON/HOST:/ABSOLUTE/PATH/ON/CONTAINER -i -t roi-img /bin/bash
```
This bind a local host directory to a directory in the container and is a good was to persist files between different invocations of this image.

The include open source softwares are: HELICS, GridLab-D and GridPACK.
