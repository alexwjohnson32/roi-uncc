#!/bin/bash

SIF_FILE="./roi-img.sif"

clear

# Purging modules to avoid loaded options that are different
module purge

apptainer exec $SIF_FILE bash -s <<'EOF' 

echo Starting 2bus-13bus Run

export UNCC_ROOT=$(pwd)

# Linking HELICS correctly
export LD_LIBRARY_PATH=/root/develop/helics/build/lib:$LD_LIBRARY_PATH

# Changing to the correct dir
cd $UNCC_ROOT/examples/2bus-13bus
mkdir -p outputs
rm -rf outputs/*

mkdir -p build
rm -rf build/*
cd build

# Build
cmake ..
make -j10

cd $UNCC_ROOT/examples/2bus-13bus

# Running example
helics run --path=gpk-gld-cosim.json

echo Run Complete
EOF