import pygame
import cv2
import carla
import numpy as np
import random
from PIL import Image
import json

import global_variables
import sensors


def create_vehicle(world):
    vehicle_bp = world.get_blueprint_library().filter(global_variables.VEHICLE)
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
    vehicle_data = read_vehicle_file('test_vehicle.json')
    attach_sensors(vehicle, vehicle_data, world)
    
    return vehicle

def read_vehicle_file(vehicle_json):
    with open(vehicle_json) as f:
        vehicle_data = json.load(f)
    
    return vehicle_data

def attach_sensors(vehicle, vehicle_data, world):
    for sensor in vehicle_data:
        if sensor == 'rgb_camera':
            global_variables.SENSOR_DICT[sensor]    = sensors.RGB_Camera(world=world, vehicle=vehicle, sensor_dict=vehicle_data['rgb_camera'])
            global_variables.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
        elif sensor == 'lidar':
            global_variables.SENSOR_DICT[sensor]    = sensors.Lidar(world=world, vehicle=vehicle, sensor_dict=vehicle_data['lidar'])
            global_variables.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
        elif sensor == 'radar':
            global_variables.SENSOR_DICT[sensor]    = sensors.Radar(world=world, vehicle=vehicle, sensor_dict=vehicle_data['radar'])
            global_variables.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))
        elif sensor == 'gnss':
            global_variables.SENSOR_DICT[sensor]    = sensors.GNSS(world=world, vehicle=vehicle, sensor_dict=vehicle_data['gnss'])
        elif sensor == 'imu':
            global_variables.SENSOR_DICT[sensor]    = sensors.IMU(world=world, vehicle=vehicle, sensor_dict=vehicle_data['imu'])
        elif sensor == 'collision':
            global_variables.SENSOR_DICT[sensor]    = sensors.Collision(world=world, vehicle=vehicle, sensor_dict=vehicle_data['collision'])
        elif sensor == 'lane_invasion':
            global_variables.SENSOR_DICT[sensor]    = sensors.Lane_Invasion(world=world, vehicle=vehicle, sensor_dict=vehicle_data['lane_invasion'])
        else:
            print('Error: Unknown sensor ', sensor)

    
def destroy_vehicle(vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor in global_variables.SENSOR_DICT:
        global_variables.SENSOR_DICT['sensor'].destroy()
    
    global_variables.SENSOR_WINDOWS.clear()
    vehicle.destroy()

def play_window(world, vehicle, main_screen):
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            main_screen.fill((127, 127, 127))  # Fill the main window with a gray background

            for idx, sensor in enumerate(global_variables.SENSOR_WINDOWS):
                sub_surface = global_variables.SENSOR_WINDOWS[sensor]
                sub_surface_width, sub_surface_height = sub_surface.get_size()

                # Calculate row and column index
                row_idx = idx // global_variables.NUM_COLS
                col_idx = idx % global_variables.NUM_COLS

                x_position = global_variables.MARGIN + col_idx * (sub_surface_width + global_variables.MARGIN)
                y_position = global_variables.MARGIN + row_idx * (sub_surface_height + global_variables.MARGIN)

                # Draw a border around each sub-surface
                pygame.draw.rect(main_screen, (50, 50, 50), (x_position - global_variables.BORDER_WIDTH, y_position - global_variables.BORDER_WIDTH,
                                                               sub_surface_width + 2 * global_variables.BORDER_WIDTH,
                                                               sub_surface_height + 2 * global_variables.BORDER_WIDTH), global_variables.BORDER_WIDTH)

                # Display each sub-surface with a margin
                main_screen.blit(sub_surface, (x_position, y_position))

                # Check if the active_img is not None before blitting it
                if sensor in global_variables.DATA_DICT and global_variables.DATA_DICT[sensor] is not None:
                    pygame_surface = pygame.surfarray.make_surface(global_variables.DATA_DICT[sensor].swapaxes(0, 1))
                    main_screen.blit(pygame_surface, (x_position, y_position))

                # Display sensor legend
                font = pygame.font.Font(None, 24)
                legend_text = font.render(sensor.capitalize(), True, (255, 255, 255))
                main_screen.blit(legend_text, (x_position + 10, y_position + sub_surface_height - 30))

            # Display GNSS data
            if 'gnss' in global_variables.DATA_DICT and global_variables.DATA_DICT['gnss'] is not None: 
                gnss_font = pygame.font.Font(None, 24)
                gnss_text = f"GNSS Sensor: Latitude {global_variables.DATA_DICT['gnss'].latitude:.6f}, Longitude {global_variables.DATA_DICT['gnss'].longitude:.6f}, Altitude {global_variables.DATA_DICT['gnss'].altitude:.6f}"
                gnss_surface = gnss_font.render(gnss_text, True, (255, 255, 255))
                main_screen.blit(gnss_surface, (global_variables.MARGIN, global_variables.IM_HEIGHT - global_variables.MARGIN))

            # Display IMU data
            if 'imu' in global_variables.DATA_DICT and global_variables.DATA_DICT['imu'] is not None:
                imu_font = pygame.font.Font(None, 24)
                imu_text = f"IMU Sensor: Acceleration {global_variables.DATA_DICT['imu'].accelerometer.x:.6f}, {global_variables.DATA_DICT['imu'].accelerometer.y:.6f}, {global_variables.DATA_DICT['imu'].accelerometer.z:.6f}," \
                           f"Gyroscope {global_variables.DATA_DICT['imu'].gyroscope.x:.6f}, {global_variables.DATA_DICT['imu'].gyroscope.y:.6f}, {global_variables.DATA_DICT['imu'].gyroscope.z:.6f}, " \
                           f"Compass {global_variables.DATA_DICT['imu'].compass:.6f}"
                imu_surface = imu_font.render(imu_text, True, (255, 255, 255))
                imu_text_rect = imu_surface.get_rect()
                imu_text_rect.topleft = (global_variables.IM_WIDTH - imu_text_rect.width - global_variables.MARGIN, global_variables.IM_HEIGHT - global_variables.MARGIN)
                main_screen.blit(imu_surface, imu_text_rect)

            pygame.display.flip()

    finally:
        destroy_vehicle(vehicle)
        pygame.quit()
        print('Bye bye')


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
    pygame.init()
    pygame.display.set_caption('Carla Sensor feed')
    main_screen = pygame.display.set_mode((global_variables.IM_WIDTH, global_variables.IM_HEIGHT))
    play_window(world, vehicle, main_screen)

if __name__ == '__main__':
    main()
