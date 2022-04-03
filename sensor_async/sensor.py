import abc
import datetime
import threading
import asyncio
import concurrent.futures


class Sensor(abc.ABC):
    '''! Provides basic structure of a sensor and its necessary functions.
    Contains essential functionality for asynchronous reading of data.
    '''

    def __init__(self, name: str) -> None:
        '''! Construct a new sensor object.

        @param name Sensor name for identification
        '''

        super().__init__()

        # arguments
        self.name = name

        # variables
        self.reading = False
        self.data = None
        self.mutex = threading.Condition()
        self.future = None
        self.valid = False

        # Setup and test the sensor
        self.config({})

    def config(self, config: dict) -> None:
        '''! Configure sensor parameters by providing a config dictionary

        @param config Dictionary containing key and value for each variable
        '''

        # Class variables
        members = [attr for attr in dir(self) if not callable(
            getattr(self, attr)) and not attr.startswith('__')]

        # Apply variable values from config dictionary
        for param in config:
            if param in members:
                try:
                    exec(f'self.{param}={config[param]}')
                except Exception as e:
                    pass

        # Setup and test the sensor
        try:
            if self.setup():
                self.valid = self.test_sensor()
        except:
            pass

    def __str__(self) -> str:
        '''! String identifier of this sensor

        @return Sensor name
        '''

        return self.name

    def get_filename(self, delta_hours: int = 1) -> str:
        '''! Construct a unique filename for a single data measurement

        @param delta_hours Time shift added to UTC
        @return File name
        '''

        timestamp = (datetime.datetime.now() +
                     datetime.timedelta(hours=delta_hours)).strftime('%Y%m%d-%H%M%S')

        return f'data_{self.name}_{timestamp}'

    def get_data_thread(self):
        '''! Get the data of a single sensor measurement. Handles simultanious access 
        of mulitple threads.

        @return Data in format dependent to sensor
        '''

        if not self.reading:
            # Actively read data from resource
            self.reading = True
            self.data = self.get_data()

            # Notify all threads that wait for data
            with self.mutex:
                self.mutex.notify_all()

            self.reading = False
        else:
            # Other thread is reading right now: Wait to be notified
            with self.mutex:
                self.mutex.wait()

        # Return data
        return self.data

    async def get_data_async(self):
        '''! Get the data of a single sensor measurement. Handles simultanious access
        of mulitple asyncio tasks.

        @return Data in format dependent to sensor
        '''

        if self.future == None or self.future.done():
            # Actively read data from resource
            loop = asyncio.get_running_loop()
            self.future = loop.create_future()

            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.data = await loop.run_in_executor(pool, self.get_data)

            # Notify other tasks that wait for data
            self.future.set_result(True)
        else:
            # Other task is reading right now: Wait to be notified
            await self.future

        return self.data

    @abc.abstractmethod
    def setup(self) -> bool:
        '''! Setup the sensor with given parameters

        @return bool True if setup was successful
        '''

        pass

    @abc.abstractmethod
    def get_data(self):
        '''! Retrieve a single measurement in default data format

        @return Data in format dependent to sensor
        '''

        pass

    @abc.abstractmethod
    def test_sensor(self) -> bool:
        '''! Test if the sensor returns valid data

        @return True if the sensor is valid
        '''

        pass

    @abc.abstractmethod
    def dump_file(self, base_path: str) -> None:
        '''! Store a single measurement as a file

        @param base_path File base path
        '''

        pass
