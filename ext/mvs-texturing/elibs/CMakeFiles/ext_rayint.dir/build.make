# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.31

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:

#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:

# Disable VCS-based implicit rules.
% : %,v

# Disable VCS-based implicit rules.
% : RCS/%

# Disable VCS-based implicit rules.
% : RCS/%,v

# Disable VCS-based implicit rules.
% : SCCS/s.%

# Disable VCS-based implicit rules.
% : s.%

.SUFFIXES: .hpux_make_needs_suffix_list

# Command-line flag to silence nested $(MAKE).
$(VERBOSE)MAKESILENT = -s

#Suppress display of executed commands.
$(VERBOSE).SILENT:

# A target that is always out of date.
cmake_force:
.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/local/bin/cmake

# The command to remove a file.
RM = /usr/local/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/zzz/code/mvs-texturing

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/zzz/code/mvs-texturing/build

# Utility rule file for ext_rayint.

# Include any custom commands dependencies for this target.
include elibs/CMakeFiles/ext_rayint.dir/compiler_depend.make

# Include the progress variables for this target.
include elibs/CMakeFiles/ext_rayint.dir/progress.make

elibs/CMakeFiles/ext_rayint: elibs/CMakeFiles/ext_rayint-complete

elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-install
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-mkdir
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-build
elibs/CMakeFiles/ext_rayint-complete: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-install
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Completed 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E make_directory /home/zzz/code/mvs-texturing/build/elibs/CMakeFiles
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/CMakeFiles/ext_rayint-complete
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-done

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-build: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "No build step for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E echo_append
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-build

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure: elibs/ext_rayint/tmp/ext_rayint-cfgcmd.txt
elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_3) "No configure step for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E echo_append
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-gitinfo.txt
elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-mkdir
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_4) "Performing download step (git clone) for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/elibs && /usr/local/bin/cmake -DCMAKE_MESSAGE_LOG_LEVEL=VERBOSE -P /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/tmp/ext_rayint-gitclone.cmake
	cd /home/zzz/code/mvs-texturing/elibs && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-install: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-build
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_5) "No install step for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E echo_append
	cd /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-build && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-install

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-mkdir:
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_6) "Creating directories for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -Dcfgdir= -P /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/tmp/ext_rayint-mkdirs.cmake
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-mkdir

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch-info.txt
elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_7) "No patch step for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E echo_append
	cd /home/zzz/code/mvs-texturing/build/elibs && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch

elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update-info.txt
elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download
	@$(CMAKE_COMMAND) -E cmake_echo_color "--switch=$(COLOR)" --blue --bold --progress-dir=/home/zzz/code/mvs-texturing/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_8) "No update step for 'ext_rayint'"
	cd /home/zzz/code/mvs-texturing/elibs/rayint && /usr/local/bin/cmake -E echo_append
	cd /home/zzz/code/mvs-texturing/elibs/rayint && /usr/local/bin/cmake -E touch /home/zzz/code/mvs-texturing/build/elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update

elibs/CMakeFiles/ext_rayint.dir/codegen:
.PHONY : elibs/CMakeFiles/ext_rayint.dir/codegen

ext_rayint: elibs/CMakeFiles/ext_rayint
ext_rayint: elibs/CMakeFiles/ext_rayint-complete
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-build
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-configure
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-download
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-install
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-mkdir
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-patch
ext_rayint: elibs/ext_rayint/src/ext_rayint-stamp/ext_rayint-update
ext_rayint: elibs/CMakeFiles/ext_rayint.dir/build.make
.PHONY : ext_rayint

# Rule to build all files generated by this target.
elibs/CMakeFiles/ext_rayint.dir/build: ext_rayint
.PHONY : elibs/CMakeFiles/ext_rayint.dir/build

elibs/CMakeFiles/ext_rayint.dir/clean:
	cd /home/zzz/code/mvs-texturing/build/elibs && $(CMAKE_COMMAND) -P CMakeFiles/ext_rayint.dir/cmake_clean.cmake
.PHONY : elibs/CMakeFiles/ext_rayint.dir/clean

elibs/CMakeFiles/ext_rayint.dir/depend:
	cd /home/zzz/code/mvs-texturing/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/zzz/code/mvs-texturing /home/zzz/code/mvs-texturing/elibs /home/zzz/code/mvs-texturing/build /home/zzz/code/mvs-texturing/build/elibs /home/zzz/code/mvs-texturing/build/elibs/CMakeFiles/ext_rayint.dir/DependInfo.cmake "--color=$(COLOR)"
.PHONY : elibs/CMakeFiles/ext_rayint.dir/depend

