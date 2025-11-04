cmake_minimum_required(VERSION 3.15)

project(Extensions)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

set(JOYSTICK_DIR "${CMAKE_CURRENT_SOURCE_DIR}/extensions/joystick")

file(GLOB JOYSTICK_SOURCE "${JOYSTICK_DIR}/src/*.c")

add_library(joystickinput SHARED ${JOYSTICK_SOURCE})

set_target_properties(joystickinput PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/dist"
    LIBRARY_OUTPUT_DIRECTORY_DEBUG "${CMAKE_CURRENT_SOURCE_DIR}/dist"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/dist"
    LIBRARY_OUTPUT_DIRECTORY_RELEASE "${CMAKE_CURRENT_SOURCE_DIR}/dist"
    PREFIX ""
)

target_compile_definitions(joystickinput PRIVATE EXPORT_FUNCTIONS)

target_compile_definitions(joystickinput PRIVATE EXPORT_FUNCTIONS)

target_include_directories(joystickinput PRIVATE
    "${JOYSTICK_DIR}/src"
    "${JOYSTICK_DIR}/inc"
)
