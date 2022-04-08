import os

import sensor_async.info as INFO


def main():
    # Get sensor objects from config file
    sensors = INFO.get_sensors_from_config('config.yaml')

    # Local directory
    base_dir = os.path.dirname(__file__)

    # Dump measurement for all configured sensors
    for sensor in sensors:
        if sensor.valid:
            sensor.dump_file(base_dir)


if __name__ == '__main__':
    main()
