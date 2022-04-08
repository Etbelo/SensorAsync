import matplotlib.pyplot as plt
import numpy as np
import matplotlib

matplotlib.use('Agg')


def plot(name, num_tasks, times, fps):
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
    ax[1].set_xlabel('Threads')
    ax[1].set_ylabel('FPS [Hz]')
    ax[1].set_xticks(threads)

    plt.savefig(name)
