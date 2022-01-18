# README

# Setup

## Setup Kinect

### Authorize devices

Copy '[scripts/99-k4a.rules](https://github.com/microsoft/Azure-Kinect-Sensor-SDK/blob/develop/scripts/99-k4a.rules)' into '/etc/udev/rules.d/'.

### Check installation

```cpp
$ k4aviwer
```

## Install KBBS package

```cpp
$ pip install . 
```