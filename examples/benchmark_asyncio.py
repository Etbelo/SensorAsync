import asyncio

from sensor_async.sensor import Sensor
from sensor_async.webcam import Webcam

from visualization.plot import plot


async def read_data_async(cond: asyncio.Condition, sensor: Sensor, verbose: bool = False):
    data = await sensor.get_data_async_asyncio(cond)

    if verbose:
        print(f'Data length: {len(data)}', flush=True)


async def n_read_sensor(cond: asyncio.Condition, n: int, sensor: Sensor, verbose: bool):
    loop = asyncio.get_running_loop()
    tasks = [loop.create_task(read_data_async(cond, sensor, verbose)) for i in range(n)]

    for task in tasks:
        await task


async def main_async(num_t: int, n: int, verbose: bool, sensor: Sensor):
    loop = asyncio.get_running_loop()
    cond = asyncio.Condition()

    times = []
    fps = []

    for t in range(1, num_t):
        times_local = []
        for i in range(n):
            t0 = loop.time()
            await n_read_sensor(cond, t, sensor, verbose)
            times_local.append(loop.time() - t0)

        time_mean = sum(times_local) / len(times_local)
        fps_mean = 1.0 / time_mean

        times.append(time_mean)
        fps.append(fps_mean)

        print(
            f'{n} loops, {t} tasks > mean_time: {time_mean:.04} [s], mean_fps: {fps_mean:.04} [Hz]',
            flush=True)

    plot(num_t, times, fps)


def main():
    NUM_T = 10
    N = 5
    VERBOSE = False

    # Sensor
    cam = Webcam(video_source=0, resolution=(1280, 720), type=Webcam.Type.V4L)

    try:
        asyncio.run(main_async(NUM_T, N, VERBOSE, cam))
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
