from threading import Thread
import timeit

import matplotlib.pyplot as plt
import numpy as np

from sensor_async.sensor import Sensor
from sensor_async.webcam import Webcam


def read_data(sensor: Sensor, verbose: bool = False):
    data = sensor.get_data_thread()

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


def plot(num_tasks, times, fps):
    threads = np.arange(1, num_tasks)
    times_np = np.array(times)
    fps_np = np.array(fps)

    fig, ax = plt.subplots(2, 1)
    fig.suptitle('Sensor Reading Performance')

    ax[0].plot(threads, times_np)
    ax[0].set_ylim([0, 1.2*np.max(times_np)])
    ax[0].set_ylabel('Time [s]')
    ax[0].set_xticks(threads)

    ax[1].plot(threads, fps_np)
    ax[1].set_ylim([0, 1.2*np.max(fps_np)])
    ax[1].set_xlabel('Concurrent Threads')
    ax[1].set_ylabel('FPS [Hz]')
    ax[1].set_xticks(threads)

    plt.show()


def main_sync(sensor: Sensor):
    NUM_T = 20
    N = 2  # Number of loops
    M = 2   # Number of repeats
    VERBOSE = False

    times = []
    fps = []

    for T in range(1, NUM_T):
        times_local = timeit.repeat(stmt=lambda: n_read_sensor(T, sensor, VERBOSE), number=N, repeat=M)
        time_mean, fps_mean = eval_times(times_local, N)

        times.append(time_mean)
        fps.append(fps_mean)

        print(
            f'{N} loops, {M} repeats, {T} threads > mean_time: {time_mean:.04} [s], mean_fps: {fps_mean:.04} [Hz]')

    plot(NUM_T, times, fps)


def main():
    cam = Webcam(video_source=1, resolution=(1280, 720), type=Webcam.Type.V4L)
    
    try:
        main_sync(cam)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
