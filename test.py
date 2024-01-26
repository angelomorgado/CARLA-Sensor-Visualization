import cv2
import carla
import numpy as np
import random
from PIL import Image
import time

# =================================== Global variables ===================================
IM_WIDTH    = 1920
IM_HEIGHT   = 1080
FPS         = 30
ACTIVE_IMG  = None
VEHICLE     = "vehicle.tesla.model3"
SENSOR_LIST = [] # The sensor objects should be stored in a persistent data structure or a global list to prevent them from being immediately destroyed when the function exits.
# ========================================================================================

def create_vehicle(world):
    vehicle_bp = world.get_blueprint_library().filter(VEHICLE)
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
    global SENSOR_LIST

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
    camera_sensor.listen(camera_sensor_callback)
    SENSOR_LIST.append(camera_sensor)

# This function decides what to do with the camera data, in the future i'll make a program to show it in real time, for now i'll just save the images
def camera_sensor_callback(data):
    global ACTIVE_IMG

    # Get the image from the data
    image = Image.frombytes('RGBA', (data.width, data.height), data.raw_data, 'raw', 'RGBA')

    # Get the timestamp for naming for example
    timestamp = data.timestamp
    
    # Convert the image to a NumPy array
    image_array = np.array(image)
    
    # Process the image
    # grayscale_image = cv2.cvtColor(image_array, cv2.COLOR_RGBA2GRAY) # For example, convert to grayscale

    # Display the processed image using Pygame
    ACTIVE_IMG = image_array

    # Save image in directory
    cv2.imwrite('data/rgb_camera/' + str(timestamp) + '.png', image_array)


def destroy_vehicle(vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor in SENSOR_LIST:
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
    
    vehicle = create_vehicle(world)
    vehicle.set_autopilot(True)

    try:
        while True:
            world.tick()
    except KeyboardInterrupt:
        print('Bye bye')
        destroy_vehicle(vehicle)

if __name__ == '__main__':
    main()
