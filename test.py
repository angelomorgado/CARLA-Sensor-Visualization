import cv2
import carla
import numpy as np
import random
from PIL import Image
import time

# =================================== Global variables ===================================
IM_WIDTH   = 1920
IM_HEIGHT  = 1080
FPS        = 30
ACTIVE_IMG = None
# ========================================================================================

def create_vehicle(world):
    vehicle_bp = world.get_blueprint_library().filter('vehicle.*')
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
    
    attach_sensors(vehicle, world)
    
    return vehicle


def attach_sensors(vehicle, world):
    # ============ RGB Camera =============
    sensor_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    # attributes
    sensor_bp.set_attribute('image_size_x', '1920')
    sensor_bp.set_attribute('image_size_y', '1080')
    sensor_bp.set_attribute('fov', '110')
    sensor_bp.set_attribute('sensor_tick', '1.0')

    # attach it to the vehicle
    # This will place the camera in the front bumper of the car
    transform = carla.Transform(carla.Location(x=0.8, z=1.7))
    camera_sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)

    # listen
    camera_sensor.listen(lambda data: camera_sensor_callback(data))

# This function decides what to do with the camera data, in the future i'll make a program to show it in real time, for now i'll just save the images
def camera_sensor_callback(data):
    global ACTIVE_IMG

    # Get the image from the data
    image = Image.frombytes('RGBA', (data.width, data.height), data.raw_data, 'raw', 'RGBA')

    # Get the timestamp for naming for example
    timestamp = data.timestamp

    # Display the processed image using Pygame
    ACTIVE_IMG = image

    # Save image in directory
    image.save(f'data/rgb_camera/{timestamp}.png')

    print('Image saved at data/rgb_camera/' + str(timestamp) + '.png')
    
def destroy_vehicle(world, vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor in vehicle.get_sensors():
        sensor.destroy()

    vehicle.destroy()


# =============================================================================================================
def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return

    # Add a loop to keep the program running for a short duration
    beggining_lock = True
    try:
        while True:
            if beggining_lock:
                vehicle = create_vehicle(world)
                vehicle.set_autopilot(True)
                beggining_lock = False
    except KeyboardInterrupt:
        pass
    finally:
        print('Bye bye')
        destroy_vehicle(world, vehicle)

if __name__ == '__main__':
    main()
