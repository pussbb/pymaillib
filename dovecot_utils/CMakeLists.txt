cmake_minimum_required(VERSION 2.8)

set(SRC_DIR .)
set ( CMAKE_C_FLAGS "-fPIC")

aux_source_directory( ${SRC_DIR} BUILD_LIB_SRC)
include_directories(${SRC_DIR})
add_library(dovecot_utils STATIC ${BUILD_LIB_SRC})


