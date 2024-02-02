import pygame
import carla
import random
import json
import os

import configuration
import sensors
import display


def create_vehicle(world):
    vehicle_bp = world.get_blueprint_library().filter(configuration.VEHICLE_MODEL)
    spawn_points = world.get_map().get_spawn_points()
    
    vehicle = None
    while vehicle is None:
        spawn_point = random.choice(spawn_points)
        transform = carla.Transform(
            spawn_point.location,
            spawn_point.rotation
        )
        try:
            vehicle = world.try_spawn_actor(random.choice(vehicle_bp), transform)
        except:
            # try again if failed to spawn vehicle
            pass
    
    # Attach sensors
    vehicle_data = read_vehicle_file(configuration.VEHICLE_SENSORS_FILE)
    attach_sensors(vehicle, vehicle_data, world)
    
    return vehicle

def read_vehicle_file(vehicle_json):
    with open(vehicle_json) as f:
        vehicle_data = json.load(f)
    
    return vehicle_data

def attach_sensors(vehicle, vehicle_data, world):
    for sensor in vehicle_data:
        if sensor == 'rgb_camera':
            configuration.SENSOR_DICT[sensor]    = sensors.RGB_Camera(world=world, vehicle=vehicle, sensor_dict=vehicle_data['rgb_camera'])
            configuration.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
            os.makedirs('data/rgb_camera', exist_ok=True)
        elif sensor == 'lidar':
            configuration.SENSOR_DICT[sensor]    = sensors.Lidar(world=world, vehicle=vehicle, sensor_dict=vehicle_data['lidar'])
            configuration.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
            os.makedirs('data/lidar', exist_ok=True)
        elif sensor == 'radar':
            configuration.SENSOR_DICT[sensor]    = sensors.Radar(world=world, vehicle=vehicle, sensor_dict=vehicle_data['radar'])
            configuration.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
            os.makedirs('data/radar', exist_ok=True)
        elif sensor == 'gnss':
            configuration.SENSOR_DICT[sensor]    = sensors.GNSS(world=world, vehicle=vehicle, sensor_dict=vehicle_data['gnss'])
        elif sensor == 'imu':
            configuration.SENSOR_DICT[sensor]    = sensors.IMU(world=world, vehicle=vehicle, sensor_dict=vehicle_data['imu'])
        elif sensor == 'collision':
            configuration.SENSOR_DICT[sensor]    = sensors.Collision(world=world, vehicle=vehicle, sensor_dict=vehicle_data['collision'])
        elif sensor == 'lane_invasion':
            configuration.SENSOR_DICT[sensor]    = sensors.Lane_Invasion(world=world, vehicle=vehicle, sensor_dict=vehicle_data['lane_invasion'])
        else:
            print('Error: Unknown sensor ', sensor)

    
def destroy_vehicle(vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor in configuration.SENSOR_DICT:
        configuration.SENSOR_DICT[sensor].destroy()
    
    configuration.SENSOR_WINDOWS.clear()
    vehicle.destroy()


def main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    # Create vehicle
    vehicle = create_vehicle(world)
    vehicle.set_autopilot(True)

    # Initialize pygame
    main_screen = display.initialize_pygame_window('Carla Sensor feed')
    display.play_window(vehicle, main_screen)

    # When terminated destroy the vehicle
    destroy_vehicle(vehicle=vehicle)

if __name__ == '__main__':
    main()
