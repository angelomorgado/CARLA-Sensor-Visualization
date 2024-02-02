# Pygame Window
IM_WIDTH             = 1920
IM_HEIGHT            = 1080
NUM_COLS             = 2  # Number of columns in the grid
NUM_ROWS             = 2  # Number of rows in the grid
MARGIN               = 30
BORDER_WIDTH         = 5

# Vehicle and Sensors attributes
SENSOR_FPS           = 30
VERBOSE              = False
VEHICLE_SENSORS_FILE = 'test_vehicle.json'
VEHICLE_MODEL        = "vehicle.tesla.model3"

# ============================ SHARED DATA (Do not modify) ============================
# Sensor list so they are stored in a persistent data structure to remain active and to be properly destroyed
SENSOR_DICT = {}

# Dict with the last data from each sensor
DATA_DICT = {}

# Dict holding the pygame subsurfaces for each displayable sensor
SENSOR_WINDOWS = {}

NON_DISPLAYABLE_SENSORS = ['gnss', 'imu', 'collision', 'lane_invasion']