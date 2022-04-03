from setuptools import setup, find_packages

setup(
    name='sensor_async',
    description='Sensor library for asynchronous reading using thread- or asyncio-workflow.',
    project_urls={
        'GitHub': 'https://github.com/Etbelo/SensorAsync'
    },
    license='MIT',
    packages=find_packages(include=['sensor_async']),
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
