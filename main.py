import carla

import display
import vehicle

def main():
    # Carla client
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    if world is None:
        print('Failed to load world')
        return
    
    # Create vehicle
    autonomous_vehicle = vehicle.create_vehicle(world)
    autonomous_vehicle.set_autopilot(True)

    # Initialize pygame
    main_screen = display.initialize_pygame_window('Carla Sensor feed')
    display.play_window(main_screen)

    # When terminated destroy the vehicle
    vehicle.destroy_vehicle(vehicle=autonomous_vehicle)

if __name__ == '__main__':
    main()
