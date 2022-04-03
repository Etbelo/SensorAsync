# SensorAsync

Sensor library for asynchronous reading using threaded or asyncio workflow. If sensors are required in asynchronous workflows, such as web servers, and multiple clients request the same resource, the same data should be automatically returned to all of them on demand and ensure that the resource is read only once.

## Setup

```shell
pip3 install -e .
```

## Examples

* Read sensor using variable number of concurrent tasks. Example uses webcam as a sensor.

```shell
cd examples
python3 async_asyncio.py
```

* Read sensor using variable number of concurrent threads. Example uses webcam as a sensor.

```shell
cd examples
python3 async_threads.py
```

* Configure sensors from `config.yaml` file and store all valid sensor measurements as files.

```shell
cd examples
python3 dump_sensors.py
```
