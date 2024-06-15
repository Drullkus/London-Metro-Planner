# Assignment 13: Holistic Route Planning

Assignment solution written by Drullkus, a student in a Spring 2024 Python course.
This project is written and tested with Python 3.10 on a 2023 MacBook Pro with the M2 Max chip.

## Usage Instructions

Launch `visualization.py` as the main file to open the graphical interface.

Given time constraints that are external of this assignment, it is written and designed to be simple.
The Metro map can be dragged around and each station, represented by circles as nodes on a graph of metro lines.

The first station clicked will be treated as the starting station, the second station clicked will become the destination.
Subsequent station selections will result in the newly-clicked station becoming the destination, while the prior destination becomes the source.

## Dependencies

The only non-standard dependency required is [DearPyGui](https://github.com/hoffstadt/DearPyGui), a Python API for creating a graphical application running ImGui.
ImGui is simple API, designed and best utilized for integrating into existing game codebases that utilize a rendering loop.
[It is battle-tested and heavily used in the Video Game Industry](https://github.com/ocornut/imgui/wiki/Software-using-dear-imgui).

Python however is not as efficient as C# or Java, let alone raw C++.
DearPyGui is more of a wrapper than a direct integration of ImGui into the Python language, thus operating on a different paradigm than of stock ImGui.
There is no support for remote display or rendering, so it must be installed on the user's machine.

[DearPyGui can be installed](https://github.com/hoffstadt/DearPyGui?tab=readme-ov-file#installation) with `pip3 install dearpygui`.
It is supported on Windows, macOS, and Linux.

No other dependencies are necessary.

## Data Sets

Datasets are sourced from [Wikimedia](https://commons.wikimedia.org/wiki/London_Underground_geographic_maps).
