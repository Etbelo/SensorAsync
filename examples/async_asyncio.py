import asyncio

import matplotlib.pyplot as plt
import numpy as np

from sensor_async.sensor import Sensor
from sensor_async.webcam import Webcam


async def read_data_async(cond: asyncio.Condition, sensor: Sensor, verbose: bool = False):
    data = await sensor.get_data_async(cond)

    if verbose:
        print(f'Data length: {len(data)}')


async def n_read_sensor(cond: asyncio.Condition, n: int, sensor: Sensor, verbose: bool):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(read_data_async(cond, sensor, verbose)) for i in range(n)]

    for task in tasks:
        await task


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


async def main_async(sensor: Sensor):
    NUM_T = 10
    N = 5
    VERBOSE = False

    loop = asyncio.get_running_loop()
    cond = asyncio.Condition()

    times = []
    fps = []

    for T in range(1, NUM_T):
        times_local = []
        for n in range(N):
            t0 = loop.time()
            await n_read_sensor(cond, T, sensor, VERBOSE)
            times_local.append(loop.time() - t0)

        time_mean = sum(times_local) / len(times_local)
        fps_mean = 1.0 / time_mean

        times.append(time_mean)
        fps.append(fps_mean)

        print(
            f'{N} loops, {T} tasks > mean_time: {time_mean:.04} [s], mean_fps: {fps_mean:.04} [Hz]')

    plot(NUM_T, times, fps)


def main():
    cam = Webcam(video_source=1, resolution=(1280, 720), type=Webcam.Type.V4L)

    try:
        asyncio.run(main_async(cam))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
