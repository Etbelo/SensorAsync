import importlib
import os
import pkgutil
import importlib
import inspect

import yaml


def get_sensors():
    '''! Get all available sensor classes from this package

    @return Dictionary with available sensor names and classes
    '''

    sensors = {}
    module_path = os.path.dirname(__file__)

    for _, name, _ in pkgutil.iter_modules([module_path]):
        module = importlib.import_module(f'sensor_async.{name}')
        classes = inspect.getmembers(module, inspect.isclass)

        for class_name, class_ in classes:
            if class_.__base__.__name__ == 'Sensor' and class_name not in sensors:
                sensors[class_name] = class_

    return sensors


def read_config(config_file):
    '''! Read yaml config file

    @return Config dictionary
    '''

    try:
        with open(config_file, 'rb') as file:
            return yaml.safe_load(file)
    except:
        pass

    return None


def sensors_from_config(config):
    # Dictionary with all available sensor names and classes
    sensors = get_sensors()

    # Sensor config file
    config = read_config('config.yaml')

    result = []

    for sensor_name in config:
        if sensor_name in sensors:
            # Configure sensor object
            sensor = sensors[sensor_name](config=config[sensor_name])

            # Test if sensor is valid and append to result
            if sensor.valid:
                result.append(sensor)

    return result
