'''
Main window:
    It acts as the center of the entire program controlling the entire process.
'''

import carla

from display import Display
from vehicle import Vehicle

def main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    # Create vehicle
    autonomous_vehicle = Vehicle(world=world)
    autonomous_vehicle.set_autopilot(True)

    # Display the vehicle's sensors
    display = Display('Carla Sensor feed', autonomous_vehicle)
    display.play_window()

    # When terminated destroy the vehicle
    autonomous_vehicle.destroy_vehicle()

if __name__ == '__main__':
    main()
