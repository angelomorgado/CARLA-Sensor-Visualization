import pygame
import cv2
import carla
import numpy as np
import random
from PIL import Image

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

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Ensure the array is contiguous in memory
    image_array = np.ascontiguousarray(image_array)
    # Convert to RGB using OpenCV function
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)

    # Process the image if needed
    # For example, convert to grayscale
    # grayscale_image = cv2.cvtColor(image_array, cv2.COLOR_RGBA2GRAY)

    # Display the processed image using Pygame
    ACTIVE_IMG = image_array

    # Save image in directory
    timestamp = data.timestamp
    cv2.imwrite(f'data/rgb_camera/{timestamp}.png', ACTIVE_IMG)
    
def destroy_vehicle(vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor in SENSOR_LIST:
        sensor.destroy()

    vehicle.destroy()

def play_window(world, vehicle, screen):
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if ACTIVE_IMG is not None:
                    pygame_surface = pygame.surfarray.make_surface(ACTIVE_IMG.swapaxes(0,1))
                    screen.blit(pygame_surface, (0,0))
                    pygame.display.flip()

            # pygame.time.Clock().tick(FPS)  # Control frame rate
            
    finally:
        destroy_vehicle(vehicle)
        pygame.quit()
        print('Bye bye')

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    vehicle = create_vehicle(world)
    vehicle.set_autopilot(True)

    pygame.init()
    pygame.display.set_caption('Carla Sensor feed')
    screen = pygame.display.set_mode((IM_WIDTH, IM_HEIGHT)) 
    play_window(world, vehicle, screen)

if __name__ == '__main__':
    main()
