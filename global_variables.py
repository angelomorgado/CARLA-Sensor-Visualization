# Pygame Window
IM_WIDTH    = 1920
IM_HEIGHT   = 1080
NUM_COLS = 2  # Number of columns in the grid
NUM_ROWS = 2  # Number of rows in the grid
MARGIN = 30
BORDER_WIDTH = 5

# Sensor last data
ACTIVE_DATA = []  # Stores the latest frame from each sensor
GNSS_DATA = None
IMU_DATA = None

# Sensor attributes
FPS         = 30
VERBOSE     = False

# Simulation attributes
VEHICLE     = "vehicle.tesla.model3"

# Sensor list so they are stored in a persistent data structure to remain active and to be properly destroyed
SENSOR_DICT = {
    'rgb_camera': None,
    'lidar': None,
    'radar': None,
    'gnss': None,
    'imu': None,
    'collision': None,
    'lane_invasion': None
}

# Dict with the last data from each sensor
DATA_DICT = {
    'rgb_camera': None,
    'lidar': None,
    'radar': None,
    'gnss': None,
    'imu': None,
    'collision': None,
    'lane_invasion': None
}

NON_DISPLAYABLE_SENSORS = ['gnss', 'imu','collision', 'lane_invasion']
# Dict holding the pygame subsurfaces for each displayable sensor
SENSOR_WINDOWS = {}