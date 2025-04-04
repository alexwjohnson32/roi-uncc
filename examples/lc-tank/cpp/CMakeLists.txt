cmake_minimum_required(VERSION 3.21)

project(LC_TANK)

add_executable(Capacitor Capacitor.cpp)
target_include_directories(Capacitor
  PRIVATE
  /usr/lib/x86_64-linux-gnu/openmpi/include
  /usr/local/ga-5.8/include
  /usr/local/GridPACK/include
  /usr/local/helics/include
  )

add_executable(Inductor Inductor.cpp)
target_include_directories(Inductor
  PRIVATE
  /usr/lib/x86_64-linux-gnu/openmpi/include
  /usr/local/ga-5.8/include
  /usr/local/GridPACK/include
  /usr/local/helics/include
  )

 # List of library names
 set(LIBRARIES_NAMES
   "mpi"
   "mpi_cxx"
   "petsc"
   "parmetis"
   "boost_random"
   "boost_serialization"
   "boost_mpi"
   "armci"
   "ga"
   "ga++"
   "gridpack_configuration"
   "gridpack_math"
   "gridpack_block_parsers"
   "gridpack_stream"
   "gridpack_components"
   "gridpack_ymatrix_components"
   "gridpack_pfmatrix_components"
   "gridpack_partition"
   "gridpack_parallel"
   "gridpack_dynamic_simulation_full_y_module"
   "gridpack_powerflow_module"
   "gridpack_environment"
   "gridpack_timer"
   "helicscpp"
   )

# Variable to hold the paths of found libraries
set(LIBRARIES_FOUND)

# Step 1: Loop through the list to find each library
foreach(LIBRARY_NAME IN LISTS LIBRARIES_NAMES)

  find_library(LIBRARY_PATH NAMES ${LIBRARY_NAME}
    PATHS /usr/local/GridPACK/lib
    /usr/local/ga-5.8/lib
    /usr/local/petsc-3.16.4/lib
    /usr/local/boost-1.78.0/lib
    /usr/lib/x86_64-linux-gnu/openmpi/lib
    /usr/local/helics/lib
    NO_CACHE
    NO_DEFAULT_PATH
    )

  # Check if the library was found
  if(NOT LIBRARY_PATH)
    message(FATAL_ERROR "Library '${LIBRARY_NAME}' could not be found.")
  endif()

  # Append the found library path to the LIBRARIES_FOUND list
  list(INSERT LIBRARIES_FOUND 0  ${LIBRARY_PATH})
  unset(LIBRARY_PATH)
endforeach()

message(STATUS "All Libraries found: ${LIBRARIES_FOUND}")

target_link_libraries(Capacitor PRIVATE ${LIBRARIES_FOUND} )
target_link_libraries(Inductor PRIVATE ${LIBRARIES_FOUND} )
