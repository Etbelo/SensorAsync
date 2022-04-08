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

        # Parameter: Threadsafe reading
        self.reading_thread = False
        self.param_lock = threading.Lock()

        # Parameter: Tasksafe reading
        self.reading_task = False
        self.param_lock_asyncio = asyncio.Lock()

        # Data
        self.data = None
        self.data_lock = threading.Lock()

        # Reading condition: Thread (Reading condition for asyncio must
        # be generated in event-loop Thread)
        self.cond = threading.Condition()

        self.future = None
        self.valid = False

    def parse_param(self, param):
        '''! Parse config parameter to be executable

        @param Raw param read from config
        @return Param in executable form
        '''

        # Restrict strings from being executed
        if isinstance(param, str):
            return f'str("{param}")'

        return param

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
                    exec(f'self.{param}={self.parse_param(config[param])}')
                except:
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

    def get_data_safe(self):
        '''!  Get the data of a single sensor measurement. Let only one thread access
        the resource at a time. Last protection measure to safely access the resource.

        @return Data in format dependent to sensor
        '''

        with self.data_lock:
            return self.get_data()

    def get_data_async_thread(self):
        '''! Get the data of a single sensor measurement. Handles simultanious access 
        of mulitple threads returning the same data.

        @return Data in format dependent to sensor
        '''

        reader = False

        # First thread to detect reading_thread==False is marked the reader
        with self.param_lock:
            if not self.reading_thread:
                reader = True
                self.reading_thread = True

        if reader:
            # Reader thread gets data (Additional read protection to be safe)
            self.data = self.get_data_safe()

            # Notify waiting threads
            with self.cond:
                self.cond.notify_all()

            # Reset reading variable
            self.reading_thread = False
        else:
            # Wait for reading to be finished (Timeout 1 second)
            with self.cond:
                self.cond.wait(1.0)

        return self.data

    async def get_data_async_asyncio(self, cond: asyncio.Condition):
        '''! Get the data of a single sensor measurement. Handles simultanious access
        of mulitple asyncio tasks returning the same data.

        @param cond Asyncio condition from working thread
        @return Data in format dependent to sensor
        '''

        reader = False

        # First task to detect reading_task==False is marked the reader
        async with self.param_lock_asyncio:
            if not self.reading_task:
                reader = True
                self.reading_task = True

        if reader:
            loop = asyncio.get_running_loop()

            # Reader task gets data (Additional read protection to be safe)
            with concurrent.futures.ThreadPoolExecutor() as pool:
                self.data = await loop.run_in_executor(pool, self.get_data_safe)

            # Notify waiting tasks
            async with cond:
                cond.notify_all()

            # Reset reading variable
            self.reading_task = False
        else:
            # Wait for reading to be finished
            async with cond:
                await cond.wait()

        return self.data

    @abc.abstractmethod
    def setup(self) -> bool:
        '''! Setup the sensor with given parameters

        @return bool True if setup was successful
        '''

        pass

    @abc.abstractmethod
    def get_data(self):
        '''! Retrieve a single measurement in default data format. No thread
        protection necessary. Reading threadsafe using get_data_safe or
        get_data_async.

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
