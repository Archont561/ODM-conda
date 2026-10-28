cmake_minimum_required(VERSION 3.15)
project(odm_pybind11_tests_disabled_check LANGUAGES CXX)

# Standalone experiment: the caller must separately verify the pinned OpenSfM
# source tree and archives. This is not the OpenSfM project or a network sandbox.
if(NOT IS_ABSOLUTE "${PYBIND11_SOURCE}" OR NOT EXISTS "${PYBIND11_SOURCE}/CMakeLists.txt")
  message(FATAL_ERROR "Set PYBIND11_SOURCE to the staged pybind11 source directory")
endif()
set(BUILD_TESTING OFF CACHE BOOL "" FORCE)
set(PYBIND11_TEST OFF CACHE BOOL "" FORCE)
set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "" FORCE)
add_subdirectory("${PYBIND11_SOURCE}" pybind11)
if(PYBIND11_TEST OR BUILD_TESTING OR EXISTS "${CMAKE_BINARY_DIR}/pybind11/tests")
  message(FATAL_ERROR "The pybind11 test tree must not be configured")
endif()
