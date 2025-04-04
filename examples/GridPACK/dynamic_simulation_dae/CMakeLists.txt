# -*- mode: cmake -*-
#
#     Copyright (c) 2013 Battelle Memorial Institute
#     Licensed under modified BSD License. A copy of this license can be
#     found
#     in the LICENSE file in the top level directory of this distribution.
#
# -------------------------------------------------------------
# file: CMakeLists.install.in
# -------------------------------------------------------------
# -------------------------------------------------------------
# Created January 28, 2014 by William A. Perkins
# Last Change: 2018-07-17 14:07:40 d3g096
# -------------------------------------------------------------

cmake_minimum_required(VERSION 2.6.4)

if (NOT GRIDPACK_DIR)
  set(GRIDPACK_DIR /usr/local/GridPACK
      CACHE PATH "GridPACK installation directory")
endif()

include("${GRIDPACK_DIR}/lib/GridPACK.cmake")

project(DynamicSimulation)

enable_language(CXX)

gridpack_setup()

add_definitions(${GRIDPACK_DEFINITIONS})
include_directories(BEFORE ${CMAKE_CURRENT_SOURCE_DIR})
include_directories(BEFORE ${GRIDPACK_INCLUDE_DIRS})

add_executable(dsim.x
   dsf_main.cpp
)

target_link_libraries(dsim.x ${GRIDPACK_LIBS})

add_custom_target(dsim.x.input
 
  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/input_9b3g.xml
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/9b3g.raw
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/9b3g.dyr
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/input_145.xml
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/IEEE_145bus_v23_PSLF.raw
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/IEEE_145b_classical_model.dyr
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/input_300_cmpld.xml
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/300bus_v23_no0imp_pslf.raw
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/300bus_detail_model_cmpld_combine.dyr
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/input_3000.xml
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/bus3000_gen_no0imp_v23_pslf.raw
  ${CMAKE_CURRENT_BINARY_DIR}

  COMMAND ${CMAKE_COMMAND} -E copy 
  ${CMAKE_CURRENT_SOURCE_DIR}/classical_model_3000bus.dyr
  ${CMAKE_CURRENT_BINARY_DIR}

  DEPENDS 
  ${CMAKE_CURRENT_SOURCE_DIR}/input_9b3g.xml
  ${CMAKE_CURRENT_SOURCE_DIR}/9b3g.raw
  ${CMAKE_CURRENT_SOURCE_DIR}/9b3g.dyr

  ${CMAKE_CURRENT_SOURCE_DIR}/input_145.xml
  ${CMAKE_CURRENT_SOURCE_DIR}/IEEE_145bus_v23_PSLF.raw
  ${CMAKE_CURRENT_SOURCE_DIR}/IEEE_145b_classical_model.dyr

  ${CMAKE_CURRENT_SOURCE_DIR}/input_300_cmpld.xml
  ${CMAKE_CURRENT_SOURCE_DIR}/300bus_v23_no0imp_pslf.raw
  ${CMAKE_CURRENT_SOURCE_DIR}/300bus_detail_model_cmpld_combine.dyr

  ${CMAKE_CURRENT_SOURCE_DIR}/input_3000.xml
  ${CMAKE_CURRENT_SOURCE_DIR}/bus3000_gen_no0imp_v23_pslf.raw
  ${CMAKE_CURRENT_SOURCE_DIR}/classical_model_3000bus.dyr
)

add_dependencies(dsim.x dsim.x.input)

