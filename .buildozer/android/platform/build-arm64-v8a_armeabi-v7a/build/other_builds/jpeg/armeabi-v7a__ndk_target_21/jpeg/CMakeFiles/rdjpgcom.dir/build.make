# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.22

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
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E rm -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg

# Include any dependencies generated for this target.
include CMakeFiles/rdjpgcom.dir/depend.make
# Include any dependencies generated by the compiler for this target.
include CMakeFiles/rdjpgcom.dir/compiler_depend.make

# Include the progress variables for this target.
include CMakeFiles/rdjpgcom.dir/progress.make

# Include the compile flags for this target's objects.
include CMakeFiles/rdjpgcom.dir/flags.make

CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o: CMakeFiles/rdjpgcom.dir/flags.make
CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o: rdjpgcom.c
CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o: CMakeFiles/rdjpgcom.dir/compiler_depend.ts
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building C object CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o"
	/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/bin/clang --target=armv7-none-linux-androideabi19 --sysroot=/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/sysroot $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -MD -MT CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o -MF CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o.d -o CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o -c /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/rdjpgcom.c

CMakeFiles/rdjpgcom.dir/rdjpgcom.c.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing C source to CMakeFiles/rdjpgcom.dir/rdjpgcom.c.i"
	/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/bin/clang --target=armv7-none-linux-androideabi19 --sysroot=/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/sysroot $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -E /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/rdjpgcom.c > CMakeFiles/rdjpgcom.dir/rdjpgcom.c.i

CMakeFiles/rdjpgcom.dir/rdjpgcom.c.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling C source to assembly CMakeFiles/rdjpgcom.dir/rdjpgcom.c.s"
	/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/bin/clang --target=armv7-none-linux-androideabi19 --sysroot=/home/captaindeathead/.buildozer/android/platform/android-ndk-r25b/toolchains/llvm/prebuilt/linux-x86_64/sysroot $(C_DEFINES) $(C_INCLUDES) $(C_FLAGS) -S /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/rdjpgcom.c -o CMakeFiles/rdjpgcom.dir/rdjpgcom.c.s

# Object files for target rdjpgcom
rdjpgcom_OBJECTS = \
"CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o"

# External object files for target rdjpgcom
rdjpgcom_EXTERNAL_OBJECTS =

rdjpgcom: CMakeFiles/rdjpgcom.dir/rdjpgcom.c.o
rdjpgcom: CMakeFiles/rdjpgcom.dir/build.make
rdjpgcom: CMakeFiles/rdjpgcom.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking C executable rdjpgcom"
	$(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/rdjpgcom.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
CMakeFiles/rdjpgcom.dir/build: rdjpgcom
.PHONY : CMakeFiles/rdjpgcom.dir/build

CMakeFiles/rdjpgcom.dir/clean:
	$(CMAKE_COMMAND) -P CMakeFiles/rdjpgcom.dir/cmake_clean.cmake
.PHONY : CMakeFiles/rdjpgcom.dir/clean

CMakeFiles/rdjpgcom.dir/depend:
	cd /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg /media/captaindeathead/HardDrive/PythonProjects/Farm_CEO/.buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/jpeg/armeabi-v7a__ndk_target_21/jpeg/CMakeFiles/rdjpgcom.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : CMakeFiles/rdjpgcom.dir/depend
