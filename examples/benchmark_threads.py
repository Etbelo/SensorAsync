from threading import Thread
import timeit

from sensor_async.sensor import Sensor
from sensor_async.webcam import Webcam


from visualization.plot import plot


def read_data(sensor: Sensor, verbose: bool = False):
    data = sensor.get_data_async_thread()

    if verbose:
        print(f'Data length: {len(data)}')


def n_read_sensor(n: int, sensor: Sensor, verbose: bool):
    threads = []

    # Create threads
    for i in range(n):
        threads.append(Thread(target=read_data, args=(sensor, verbose), daemon=True))

    # Start all threads
    for thread in threads:
        thread.start()

    # Join all threads
    for thread in threads:
        thread.join()


def eval_times(times, N):
    times_ = [time / N for time in times]
    time_mean = sum(times_) / len(times_)
    fps_mean = 1.0 / time_mean

    return time_mean, fps_mean


def main_sync(num_t: int, n: int, m: int, verbose: bool, sensor: Sensor):
    times = []
    fps = []

    for t in range(1, num_t):
        times_local = timeit.repeat(
            stmt=lambda: n_read_sensor(t, sensor, verbose),
            number=n, repeat=m)
        time_mean, fps_mean = eval_times(times_local, n)

        times.append(time_mean)
        fps.append(fps_mean)

        print(
            f'{n} loops, {m} repeats, {t} threads > mean_time: {time_mean:.04} [s], mean_fps: {fps_mean:.04} [Hz]')

    plot(num_t, times, fps)


def main():
    NUM_T = 20
    N = 2  # Number of loops
    M = 2   # Number of repeats
    VERBOSE = False

    # Sensor
    cam = Webcam(video_source=0, resolution=(1280, 720), type=Webcam.Type.V4L)

    try:
        main_sync(NUM_T, N, M, VERBOSE, cam)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
