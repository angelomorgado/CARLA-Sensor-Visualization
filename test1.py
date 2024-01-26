import carla
import random
from PIL import Image


active_sensors = []

def main_menu(world):
    while True: 
        print('===========================================')
        print('Sensor Test:')
        print('0 Spawn vehicle')
        print('1 Delete vehicle')
        print('-1 Exit')
        print('===========================================')

        option = int(input('Insert option-> '))
        if option == 0:
            vehicle = spawn_vehicle(world)
            vehicle.set_autopilot(True)
        elif option == 1:
            world.get_actors().filter('vehicle.*')[0].destroy()
        elif option == -1:
            quit(0)

def spawn_vehicle(world):
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
    active_sensors.append(camera_sensor)

# This function decides what to do with the camera data, in the future i'll make a program to show it in real time, for now i'll just save the images
def camera_sensor_callback(data):
    # Get the image from the data
    image = Image.frombytes('RGBA', (data.width, data.height), data.raw_data, 'raw', 'RGBA')
    # Get the timestamp
    timestamp = data.timestamp
    # Save the image
    image.save('data/rgb_camera/{}.png'.format(timestamp))


if __name__ == '__main__':
    client = carla.Client('localhost', 2000)

    client.set_timeout(10.0)
    world = client.get_world()

    main_menu(world)