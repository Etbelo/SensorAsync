import json
import re
import os

from sensor_async.sensor import Sensor


class SystemResource(Sensor):
    '''! Read system resource from file using pattern and converter
    to return its values.
    '''

    def __init__(self, name: str, files: list, pattern: str, converter: str) -> None:
        '''! Construct a new SystemResource objec

        @param name Sensor name for identification
        @param files List of system resources
        @param pattern Regex-pattern to extract raw value
        @param converter Python code to convert data to expected output format
        '''

        self.files = files
        self.pattern = pattern
        self.converter = converter

        super().__init__(name)

    def read_file(self, file):
        '''! Read system file and convert it to expected output format

        @param file File to be read
        '''

        try:
            with open(file) as sensor:
                # Extract data using Regex
                data = re.search(self.pattern, sensor.read())

            if data is not None:
                # Convert to format using python code execution
                return exec(self.converter.replace('data', str(data)))
        except:
            pass

    def setup(self) -> bool:
        '''! Setup the SystemResource with given parameters

        @return True if setup was successful
        '''

        return True

    def get_data(self):
        '''! Retrieve a single system resource measurement

        @return Data dictionary in json format
        '''

        data = {}

        for i in range(len(self.files)):
            value = self.read_file(self.files[i])
            data[f'{self.name}_{i}'] = value

        return json.dumps(data)

    def test_sensor(self) -> bool:
        '''! Test if the sensor returns valid data

        @return True if sensor is valid
        '''

        data = self.get_data()

        return len(data) > 0

    def dump_file(self, base_path: str) -> None:
        '''! Store a single measurement as a file

        @param base_path File base path
        '''

        data = self.get_data()

        filename = os.path.join(base_path, self.get_filename() + '.json')

        try:
            with open(filename, 'w') as file:
                json.dump(data, file)
        except:
            pass
