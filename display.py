import pygame
import configuration

def initialize_pygame_window(title):
    pygame.init()
    pygame.display.set_caption(title)

    # Initialize the sensor windows
    for sensor in configuration.SENSOR_DICT:
        if sensor not in configuration.NON_DISPLAYABLE_SENSORS:
            configuration.SENSOR_WINDOWS[sensor] = pygame.Surface((640, 360))

    return pygame.display.set_mode((configuration.IM_WIDTH, configuration.IM_HEIGHT))

def play_window(main_screen):
    clock = pygame.time.Clock()  # Create a clock object to control the frame rate

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

            main_screen.fill((127, 127, 127))  # Fill the main window with a gray background

            for idx, sensor in enumerate(configuration.SENSOR_WINDOWS):
                sub_surface = configuration.SENSOR_WINDOWS[sensor]
                sub_surface_width, sub_surface_height = sub_surface.get_size()

                # Calculate row and column index
                row_idx = idx // configuration.NUM_COLS
                col_idx = idx % configuration.NUM_COLS

                x_position = configuration.MARGIN + col_idx * (sub_surface_width + configuration.MARGIN)
                y_position = configuration.MARGIN + row_idx * (sub_surface_height + configuration.MARGIN)

                # Draw a border around each sub-surface
                pygame.draw.rect(main_screen, (50, 50, 50), (x_position - configuration.BORDER_WIDTH, y_position - configuration.BORDER_WIDTH,
                                                               sub_surface_width + 2 * configuration.BORDER_WIDTH,
                                                               sub_surface_height + 2 * configuration.BORDER_WIDTH), configuration.BORDER_WIDTH)

                # Display each sub-surface with a margin
                main_screen.blit(sub_surface, (x_position, y_position))

                # Check if the active_img is not None before blitting it
                if sensor in configuration.DATA_DICT and configuration.DATA_DICT[sensor] is not None:
                    pygame_surface = pygame.surfarray.make_surface(configuration.DATA_DICT[sensor].swapaxes(0, 1))
                    main_screen.blit(pygame_surface, (x_position, y_position))

                # Display sensor legend
                font = pygame.font.Font(None, 24)
                legend_text = font.render(sensor.capitalize(), True, (255, 255, 255))
                main_screen.blit(legend_text, (x_position + 10, y_position + sub_surface_height - 30))

            # Display GNSS data
            if 'gnss' in configuration.DATA_DICT and configuration.DATA_DICT['gnss'] is not None: 
                gnss_font = pygame.font.Font(None, 24)
                gnss_text = f"GNSS Sensor: Latitude {configuration.DATA_DICT['gnss'].latitude:.6f}, Longitude {configuration.DATA_DICT['gnss'].longitude:.6f}, Altitude {configuration.DATA_DICT['gnss'].altitude:.6f}"
                gnss_surface = gnss_font.render(gnss_text, True, (255, 255, 255))
                main_screen.blit(gnss_surface, (configuration.MARGIN, configuration.IM_HEIGHT - configuration.MARGIN))

            # Display IMU data
            if 'imu' in configuration.DATA_DICT and configuration.DATA_DICT['imu'] is not None:
                imu_font = pygame.font.Font(None, 24)
                imu_text = f"IMU Sensor: Acceleration {configuration.DATA_DICT['imu'].accelerometer.x:.6f}, {configuration.DATA_DICT['imu'].accelerometer.y:.6f}, {configuration.DATA_DICT['imu'].accelerometer.z:.6f}," \
                           f"Gyroscope {configuration.DATA_DICT['imu'].gyroscope.x:.6f}, {configuration.DATA_DICT['imu'].gyroscope.y:.6f}, {configuration.DATA_DICT['imu'].gyroscope.z:.6f}, " \
                           f"Compass {configuration.DATA_DICT['imu'].compass:.6f}"
                imu_surface = imu_font.render(imu_text, True, (255, 255, 255))
                imu_text_rect = imu_surface.get_rect()
                imu_text_rect.topleft = (configuration.IM_WIDTH - imu_text_rect.width - configuration.MARGIN, configuration.IM_HEIGHT - configuration.MARGIN)
                main_screen.blit(imu_surface, imu_text_rect)

            pygame.display.flip()

            # Limit the frame rate to SENSOR_FPS
            clock.tick(configuration.SENSOR_FPS)

    finally:
        pygame.quit()
        print('Bye bye')