# IIoT Example Scripts
These scripts publish dummy data to the MQTT broker for testing purposes.

## Topics Reference

factory_name/assembly_line_number/machine_name/metric_name

- factory_name: The name of the factory
- assembly_line_number: The number of the assembly line
- machine_name: The name of the machine
- metric_name: The name of the metric

## Sensor scripts

- `sensors/temperature.py`: Publishes `motor_temperature`
- `sensors/conveyor_speed.py`: Publishes `conveyor_speed` (mostly uniform speed with very small variations)
- `sensors/acoustic_sensor.py`: Publishes `acoustic_db` (mostly uniform around -2.2 dB with very small variations)


## Resouces
- [MQTT in Python](https://www.emqx.com/en/blog/how-to-use-mqtt-in-python)