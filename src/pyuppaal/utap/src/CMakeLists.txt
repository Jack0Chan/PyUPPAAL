cmake_minimum_required(VERSION 3.5)
project(Tracer VERSION 1.1.0)

# Set CMAKE_OSX_ARCHITECTURES to build for both x86_64 and arm64
set(CMAKE_OSX_ARCHITECTURES "x86_64;arm64" CACHE STRING "Build architectures for Mac OS X" FORCE)

# Specify the C++ standard
set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED True)

# Add the executable
add_executable(tracer_darwin tracer_custom.cpp)

# Include directories
target_include_directories(tracer_darwin PRIVATE 
${CMAKE_CURRENT_SOURCE_DIR})

# If there are any libraries you need to link to, use the following command
# target_link_libraries(tracer_darwin PRIVATE some_library)



#After the build is complete, you can check if your binary is a universal binary using the lipo command.
#lipo -info tracer.app
