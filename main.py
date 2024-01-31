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
ACTIVE_DATA = []  # Stores the latest frame from each sensor
GNSS_DATA = None
IMU_DATA = None
VEHICLE     = "vehicle.tesla.model3"
SENSOR_LIST = []  # The sensor objects should be stored in a persistent data structure or a global list
BORDER_WIDTH = 5
MARGIN = 30
NUM_COLS = 2  # Number of columns in the grid
NUM_ROWS = 2  # Number of rows in the grid
# ========================================================================================

SENSOR_DICT = {
    '0': 'RGB Camera',
    '1': 'LiDAR',
    '2': 'Radar'
}

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
    global ACTIVE_DATA

    # ============ RGB Camera =============
    sensor_bp = world.get_blueprint_library().find('sensor.camera.rgb')
    # attributes
    sensor_bp.set_attribute('image_size_x', '640')
    sensor_bp.set_attribute('image_size_y', '360')
    sensor_bp.set_attribute('fov', '110')
    sensor_bp.set_attribute('sensor_tick', '0.0')

    # attach it to the vehicle
    # This will place the camera in the front bumper of the car
    transform = carla.Transform(carla.Location(x=0.8, z=1.7))
    camera_sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)

    # listen
    ACTIVE_DATA.append(None)
    camera_sensor.listen(lambda data: camera_sensor_callback(data, 0))
    SENSOR_LIST.append((camera_sensor, pygame.Surface((640, 360))))  # Store the sensor and its associated Pygame sub-surface

    # ============ LiDAR =============
    sensor_bp = world.get_blueprint_library().find('sensor.lidar.ray_cast')
    # attributes
    sensor_bp.set_attribute('channels', '64')  # Increase the number of channels
    sensor_bp.set_attribute('points_per_second', '1000000')  # Increase point density
    sensor_bp.set_attribute('rotation_frequency', '50.0')
    sensor_bp.set_attribute('upper_fov', '20.0')  # Adjust FOV to cover a larger area
    sensor_bp.set_attribute('lower_fov', '-20.0')  # Adjust FOV to cover a larger area
    sensor_bp.set_attribute('range', '100.0')  # Increase the range for better coverage
    sensor_bp.set_attribute('sensor_tick', '0.0')

    # attach it to the vehicle
    # This will place the camera in the front bumper of the car
    transform = carla.Transform(carla.Location(x=0.8, z=1.7))
    lidar_sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)

    # listen
    ACTIVE_DATA.append(None)
    lidar_sensor.listen(lambda data: lidar_sensor_callback(data, 1))
    SENSOR_LIST.append((lidar_sensor, pygame.Surface((640, 360))))  # Store the sensor and its associated Pygame sub-surface

    # ============ Radar =============
    sensor_bp = world.get_blueprint_library().find('sensor.other.radar')
    # attributes
    sensor_bp.set_attribute('horizontal_fov', '30.0')
    sensor_bp.set_attribute('vertical_fov', '30.0')
    sensor_bp.set_attribute('points_per_second', '1500')
    sensor_bp.set_attribute('range', '100')
    sensor_bp.set_attribute('sensor_tick', '0.0')

    # attach it to the vehicle
    # This will place the camera in the front bumper of the car
    transform = carla.Transform(carla.Location(x=0.8, z=1.7))
    radar_sensor = world.spawn_actor(sensor_bp, transform, attach_to=vehicle)

    # listen
    ACTIVE_DATA.append(None)
    radar_sensor.listen(lambda data: radar_sensor_callback(data, 2))
    SENSOR_LIST.append((radar_sensor, pygame.Surface((640, 360))))  # Store the sensor and its associated Pygame sub-surface


    # ============ GNSS =============
    gnss_bp = world.get_blueprint_library().find('sensor.other.gnss')
    gnss_location = carla.Location(0,0,0)
    gnss_rotation = carla.Rotation(0,0,0)
    gnss_transform = carla.Transform(gnss_location,gnss_rotation)
    gnss_bp.set_attribute("sensor_tick",str(0.1))
    ego_gnss = world.spawn_actor(gnss_bp,gnss_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
    ego_gnss.listen(lambda gnss: gnss_callback(gnss))
    SENSOR_LIST.append((ego_gnss, None))

    # ============ IMU =============
    imu_bp = world.get_blueprint_library().find('sensor.other.imu')
    imu_location = carla.Location(0,0,0)
    imu_rotation = carla.Rotation(0,0,0)
    imu_transform = carla.Transform(imu_location,imu_rotation)
    imu_bp.set_attribute("sensor_tick",str(0.1))
    ego_imu = world.spawn_actor(imu_bp,imu_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
    ego_imu.listen(lambda imu: imu_callback(imu))
    SENSOR_LIST.append((ego_imu, None)) 

    # ============ Collision =============
    collision_bp = world.get_blueprint_library().find('sensor.other.collision')
    collision_location = carla.Location(0,0,0)
    collision_rotation = carla.Rotation(0,0,0)
    collision_transform = carla.Transform(collision_location,collision_rotation)
    ego_collision = world.spawn_actor(collision_bp,collision_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
    ego_collision.listen(lambda collision: collision_callback(collision))
    SENSOR_LIST.append((ego_collision, None))


def camera_sensor_callback(data, idx):
    global ACTIVE_DATA

    # Get the image from the data
    image = Image.frombytes('RGBA', (data.width, data.height), data.raw_data, 'raw', 'RGBA')

    # Convert the image to a NumPy array
    image_array = np.array(image)

    # Ensure the array is contiguous in memory
    image_array = np.ascontiguousarray(image_array)
    # Convert to RGB using OpenCV function
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)

    # Display the processed image using Pygame
    ACTIVE_DATA[idx] = image_array

    # Save image in directory
    # timestamp = data.timestamp
    # cv2.imwrite(f'data/rgb_camera/{timestamp}.png', ACTIVE_IMG)


def lidar_sensor_callback(data, idx):
    global ACTIVE_DATA

    # Get the LiDAR point cloud from the data
    lidar_data = data.raw_data
    lidar_data = np.frombuffer(lidar_data, dtype=np.dtype('f4'))
    lidar_data = np.reshape(lidar_data, (int(lidar_data.shape[0] / 4), 4))

    # Extract X, Y, Z coordinates and intensity values
    points_xyz = lidar_data[:, :3]
    intensity = lidar_data[:, 3]

    # Intensity scaling factor
    intensity_scale = 10.0  # Adjust this value to control the brightness

    # Create a 2D histogram with a predetermined size
    width, height = 640, 360
    lidar_image_array = np.zeros((height, width))

    # Scale and shift X and Y coordinates to fit within the histogram size
    x_scaled = ((points_xyz[:, 0] + 50) / 100) * (width - 1)
    y_scaled = ((points_xyz[:, 1] + 50) / 100) * (height - 1)

    # Round the scaled coordinates to integers
    x_indices = np.round(x_scaled).astype(int)
    y_indices = np.round(y_scaled).astype(int)

    # Clip the indices to stay within the image bounds
    x_indices = np.clip(x_indices, 0, width - 1)
    y_indices = np.clip(y_indices, 0, height - 1)

    # Assign scaled intensity values to the corresponding pixel in the histogram
    lidar_image_array[y_indices, x_indices] = intensity * intensity_scale

    # Clip the intensity values to stay within the valid color range
    lidar_image_array = np.clip(lidar_image_array, 0, 255)

    ACTIVE_DATA[idx] = lidar_image_array

    # Save image in directory
    # timestamp = data.timestamp
    # cv2.imwrite(f'data/lidar/{timestamp}.png', ACTIVE_LIDAR)


def radar_sensor_callback(data, idx):
    global ACTIVE_DATA

    # Get the radar data
    radar_data = data.raw_data
    points = np.frombuffer(radar_data, dtype=np.dtype('f4'))
    points = np.reshape(points, (len(data), 4))

    # Extract information from radar points
    azimuths = points[:, 1]
    depths = points[:, 3]

    # Create a 2D histogram with a predetermined size
    width, height = 640, 360
    radar_image_array = np.zeros((height, width))

    # Scale azimuth values to fit within the histogram size
    azimuth_scaled = ((np.degrees(azimuths) + 180) / 360) * (width - 1)

    # Scale depth values to fit within the histogram size
    depth_scaled = (depths / 100) * (height - 1)

    # Round the scaled azimuth and depth values to integers
    azimuth_indices = np.round(azimuth_scaled).astype(int)
    depth_indices = np.round(depth_scaled).astype(int)

    # Clip the indices to stay within the image bounds
    azimuth_indices = np.clip(azimuth_indices, 0, width - 1)
    depth_indices = np.clip(depth_indices, 0, height - 1)

    # Set a value (e.g., velocity) at each (azimuth, depth) coordinate in the histogram
    radar_image_array[depth_indices, azimuth_indices] = 255  # Set a constant value for visibility

    ACTIVE_DATA[idx] = radar_image_array[::-1]

    # Save image in directory
    # timestamp = data.timestamp
    # cv2.imwrite(f'data/radar/{timestamp}.png', ACTIVE_DATA[idx])

def gnss_callback(data):
    global GNSS_DATA
    GNSS_DATA = data

def imu_callback(data):
    global IMU_DATA
    IMU_DATA = data

# Activates each frame a collision is occuring
def collision_callback(data):
    print(f"Collision Occurred with intensity {data.intensity} at {data.timestamp} with {data.other_actor}")


    
def destroy_vehicle(vehicle):
    vehicle.set_autopilot(False)

    # Destroy sensors
    for sensor, screen in SENSOR_LIST:
        sensor.destroy()
        screen = None

    vehicle.destroy()

def play_window(world, vehicle, main_screen):
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            main_screen.fill((127, 127, 127))  # Fill the main window with a gray background

            for idx, (sensor, sub_surface) in enumerate(SENSOR_LIST[:-3]):
                sub_surface_width, sub_surface_height = sub_surface.get_size()

                # Calculate row and column index
                row_idx = idx // NUM_COLS
                col_idx = idx % NUM_COLS

                x_position = MARGIN + col_idx * (sub_surface_width + MARGIN)
                y_position = MARGIN + row_idx * (sub_surface_height + MARGIN)

                # Draw a border around each sub-surface
                pygame.draw.rect(main_screen, (50, 50, 50), (x_position - BORDER_WIDTH, y_position - BORDER_WIDTH,
                                                               sub_surface_width + 2 * BORDER_WIDTH,
                                                               sub_surface_height + 2 * BORDER_WIDTH), BORDER_WIDTH)

                # Display each sub-surface with a margin
                main_screen.blit(sub_surface, (x_position, y_position))

                # Check if the active_img is not None before blitting it
                if ACTIVE_DATA[idx] is not None:
                    pygame_surface = pygame.surfarray.make_surface(ACTIVE_DATA[idx].swapaxes(0, 1))
                    main_screen.blit(pygame_surface, (x_position, y_position))

                # Display sensor legend
                font = pygame.font.Font(None, 24)
                legend_text = font.render(SENSOR_DICT[str(idx)], True, (255, 255, 255))
                main_screen.blit(legend_text, (x_position + 10, y_position + sub_surface_height - 30))

            # Display GNSS data
            if GNSS_DATA is not None:
                gnss_font = pygame.font.Font(None, 24)
                gnss_text = f"GNSS Sensor: Latitude {GNSS_DATA.latitude:.6f}, Longitude {GNSS_DATA.longitude:.6f}, Altitude {GNSS_DATA.altitude:.6f}"
                gnss_surface = gnss_font.render(gnss_text, True, (255, 255, 255))
                main_screen.blit(gnss_surface, (MARGIN, IM_HEIGHT - MARGIN))

            # Display IMU data
            if IMU_DATA is not None:
                imu_font = pygame.font.Font(None, 24)
                imu_text = f"IMU Sensor: Acceleration {IMU_DATA.accelerometer.x:.6f}, {IMU_DATA.accelerometer.y:.6f}, {IMU_DATA.accelerometer.z:.6f}," \
                           f"Gyroscope {IMU_DATA.gyroscope.x:.6f}, {IMU_DATA.gyroscope.y:.6f}, {IMU_DATA.gyroscope.z:.6f}, " \
                           f"Compass {IMU_DATA.compass:.6f}"
                imu_surface = imu_font.render(imu_text, True, (255, 255, 255))
                imu_text_rect = imu_surface.get_rect()
                imu_text_rect.topleft = (IM_WIDTH - imu_text_rect.width - MARGIN, IM_HEIGHT - MARGIN)
                main_screen.blit(imu_surface, imu_text_rect)

            pygame.display.flip()

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
    main_screen = pygame.display.set_mode((IM_WIDTH, IM_HEIGHT))
    play_window(world, vehicle, main_screen)

if __name__ == '__main__':
    main()
