rm -rf build

mkdir build
cp dsf_main.cpp build/
# Copy configuration file
cp input_145.xml build/input.xml
# Copy network configuraion file 
cp IEEE_145bus_v23_PSLF.raw build/IEEE_145bus_v23_PSLF.raw
# Copy device parameter file
cp IEEE_145b_classical_model.dyr build/IEEE_145b_classical_model.dyr
cd build

g++ -c dsf_main.cpp -I/usr/lib/x86_64-linux-gnu/openmpi/include \
    -I/usr/local/ga-5.8/include\
    -I/usr/local/GridPACK/include

g++ dsf_main.o \
    -L/usr/local/GridPACK/lib \
        -lgridpack_timer \
        -lgridpack_environment \
	-lgridpack_powerflow_module \
	-lgridpack_dynamic_simulation_full_y_module \
	-lgridpack_parallel \
	-lgridpack_partition \
	-lgridpack_pfmatrix_components \
	-lgridpack_ymatrix_components \
	-lgridpack_components \
	-lgridpack_stream \
	-lgridpack_block_parsers \
	-lgridpack_math \
	-lgridpack_configuration \
    -L/usr/local/ga-5.8/lib -lga++ -lga -larmci \
    -L/usr/local/boost-1.78.0/lib -lboost_mpi -lboost_serialization \
        -lboost_random \
    /usr/local/petsc-3.16.4/lib/libparmetis.so \
    /usr/local/petsc-3.16.4/lib/libpetsc.so.3.16 \
    -L/usr/lib/x86_64-linux-gnu/openmpi/lib -lmpi_cxx -lmpi \
    -o dsf_main.x
