# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "/home/zzz/code/mvs-texturing/elibs/mapmap")
  file(MAKE_DIRECTORY "/home/zzz/code/mvs-texturing/elibs/mapmap")
endif()
file(MAKE_DIRECTORY
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src/ext_mapmap-build"
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap"
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/tmp"
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src/ext_mapmap-stamp"
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src"
  "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src/ext_mapmap-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src/ext_mapmap-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "/home/zzz/code/mvs-texturing/build/elibs/ext_mapmap/src/ext_mapmap-stamp${cfgdir}") # cfgdir has leading slash
endif()
