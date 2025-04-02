#!/bin/bash

SIF_FILE="./roi-img.sif"

clear

# Purging modules to avoid loaded options that are different
module purge

apptainer exec $SIF_FILE bash -s <<'EOF' 

echo Starting lc-tank Run

export UNCC_ROOT=$(pwd)

# Linking HELICS correctly
export LD_LIBRARY_PATH=/root/develop/helics/build/lib:$LD_LIBRARY_PATH

# Changing to the correct dir
cd $UNCC_ROOT/examples/lc-tank
mkdir -p outputs
rm -rf outputs/*

cd $UNCC_ROOT/examples/lc-tank/cpp

# Build Directory
mkdir -p build
rm -rf build/*
cd build

# Build
cmake  ..
make -j10

# Change the json file if needed
sed -i 's|\./Inductor|./build/Inductor|g; s|\./Capacitor|./build/Capacitor|g' $UNCC_ROOT/examples/lc-tank/cpp/lc-tank-cpp.json

# Running example
cd $UNCC_ROOT/examples/lc-tank/cpp
helics run --path=lc-tank-cpp.json

echo Run Complete
EOF