import pygame
import cv2
import carla
import numpy as np
import random
from PIL import Image

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

    # Convert the image to a NumPy array
    image_array = np.array(image)
    
    # Process the image
    # grayscale_image = cv2.cvtColor(image_array, cv2.COLOR_RGBA2GRAY) # For example, convert to grayscale

    # Display the processed image using Pygame
    ACTIVE_IMG = image_array

    # Save image in directory
    cv2.imwrite('data/rgb_camera/' + str(timestamp) + '.png', image_array)
    
def destroy_sensors(world):
    actors = world.get_actors()
    for actor in actors:
        if actor.type_id == 'sensor.camera.rgb':
            actor.destroy()

# def play_window(world, vehicle, screen):
#     try:
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     return
                
#                 if ACTIVE_IMG is not None:
#                     pygame_surface = pygame.surfarray.make_surface(ACTIVE_IMG.swapaxes(0, 1))
#                     screen.blit(pygame_surface, (0,0))
#                     pygame.display.flip()

#             pygame.time.Clock().tick(FPS)  # Control frame rate
            
#     finally:
#         destroy_sensors(world)
#         vehicle.destroy()
#         pygame.quit()
#         print('Bye bye')

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    frame = 0
    vehicle = create_vehicle(world)

    # pygame.init()
    # pygame.display.set_caption('Carla Sensor feed')
    # screen = pygame.display.set_mode((IM_WIDTH, IM_HEIGHT)) 
    # play_window(world, vehicle, screen)

if __name__ == '__main__':
    main()
