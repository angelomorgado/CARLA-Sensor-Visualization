# Carla Sensor Visualization

Allows to visualize an ego vehicle's sensors using PyGame.

![](gifs/sensor-visualizer.gif)

It is dynamic, being able to create new vehicle configurations based on Json files.

---

## To Run the Project

1. It is recommended to use a virtual environment with python 3.8. 
2. Install the requirements with `pip install -r requirements.txt`
3. Run the CARLA server with the desired map
4. Run the project with `python main.py`

---

## Modules

- `main.py`: Main file, controls the entire process
- `display.py`: Contains the methods to display the sensors in a PyGame window
- `vehicle.py`: Contains the methods responsible for creating the ego vehicle, attaching sensors to it, destroying it, and in future versions, controlling it
- `sensors.py`: Contains classes for each sensor, with methods to attach them to the vehicle, and to get their data through callbacks
- 'config.py': Contains option parameters for the simulation

These modules are coded to be extremely dynamic, allowing their integration with any other project.

---

## Sensors

Available sensors:
- RGB Camera
- LiDAR
- Radar
- GNSS
- IMU
- Collision
- Lane Invasion

Future sensors:
- Semantic Segmentation Camera
- Instance Segmentation Camera
- Depth Camera
- Lidar Semantic Segmentation
- Obstacle Detection
- Optical Flow Camera (AKA: Motion Camera)

The collision and lane invasion sensors are special in the way that they are only triggered when the vehicle collides with something or invades a lane, respectively. And their information is not displayed in the PyGame window, but in the terminal.

---

## TODO

- Maybe make a web client of this that lets you chose different vehicles and verify if they have sensors and all. Cool idea.

- Add the rest of the available CARLA sensors

- Make the window dynamic based on the amount of sensors

