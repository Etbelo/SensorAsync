from setuptools import setup

setup(
    name='sensor_async',
    description='Sensor library for asynchronous reading using thread- or asyncio-workflow.',
    author='Johann Erhard',
    zip_safe=False,
    install_requires=[
        'matplotlib',
        'numpy',
        'opencv_python',
        'PyTurboJPEG',
        'PyYAML',
        'setuptools',
        'v4l2py'
    ]
)
