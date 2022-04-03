import enum
import platform
import os


from sensor_async.sensor import Sensor

if platform.system() == 'Linux':
    import v4l2py

import cv2
import turbojpeg


class Webcam(Sensor):
    '''! Read images from webcam or other video source using two different drivers.
    '''

    class Type(enum.Enum):
        '''! Driver type'''

        OpenCV = 1
        V4L = 2

    def __init__(
            self, name: str = 'webcam', video_source: int = 0, resolution: tuple = (1080, 720),
            type: Type = Type.V4L) -> None:
        '''! Construct a new Webcam object

        @param name Sensor name for identification
        @param video_source Local video source id
        @param resolution Webcam resolution for reading
        @param type Webcam driver selection
        '''

        self.video_source = video_source
        self.resolution = resolution
        self.type = type.value

        # Type selection
        if platform.system() == 'Windows':
            self.type = Webcam.Type.OpenCV.value

        super().__init__(name)

    def setup(self) -> bool:
        '''! Setup the Webcam with given parameters

        @return True if setup was successful
        '''

        if self.type == Webcam.Type.OpenCV.value:
            self.video_cap = cv2.VideoCapture(self.video_source)
            self.video_cap.set(cv2.CAP_PROP_FOURCC, 0x47504A4D)
            self.video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.encoder = turbojpeg.TurboJPEG()
            return True

        if self.type == Webcam.Type.V4L.value:
            device = v4l2py.Device.from_id(self.video_source)
            device.video_capture.set_format(
                self.resolution[0], self.resolution[1], 'MJPG')
            self.video_cap = iter(device)
            return True

        return False

    def get_data(self) -> bytes:
        '''! Retrieve a single image in encoded jpg format

        @return JPG image in bytes
        '''

        data = bytearray()

        try:
            if self.type == Webcam.Type.OpenCV.value:
                frame = self.video_cap.read()[1]
                data = self.encoder.encode(frame)

            if self.type == Webcam.Type.V4L.value:
                data = next(self.video_cap)
        except Exception as e:
            print(e)

        return data

    def test_sensor(self) -> bool:
        '''! Test if the sensor returns valid data

        @return True if the Webcam is valid
        '''

        data = self.get_data()

        return len(data) > 0

    def dump_file(self, base_path: str = '') -> None:
        '''! Store a single image as a file

        @param base_path File base path
        '''

        data = self.get_data()

        filename = os.path.join(base_path, self.get_filename() + '.jpg')

        try:
            with open(filename, 'wb') as file:
                file.write(data)
        except:
            pass
