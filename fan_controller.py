import os
import subprocess
import time

amd_cpu = "k10temp"
cpu_temp_sensor = "temp1_input"
amd_gpu = "amdgpu"
gpu_temp_sensor = "temp1_input"
# gpu_1_id = "f4ae5c2ae0aec465"
gpu_2_id = "4d91a42a85aa9594"
# gpu_1_id = "a13b51a602c8c61a"
# gpu_2_id = "f9a16304bb24194e"
gpu_1_id = "680d990547b89c6d"


# temperature in degrees
min_temperature = 45
max_temperature = 77

min_cpu_temperature = 40
max_cpu_temperature = 77

# fan speed in percentage
min_fan_speed = 27
max_fan_speed = 100

min_cpu_fan_speed = 20
max_cpu_fan_speed = 100

exp = 3
gpu_factor = (max_fan_speed - min_fan_speed) / ((max_temperature - min_temperature) ** exp)
cpu_factor = (max_cpu_fan_speed - min_cpu_fan_speed) / ((max_cpu_temperature - min_cpu_temperature) ** exp)


def get_nv_temp():
    try:

        result =  (subprocess.run(['nvidia-smi', '-i', '00000000:81:00.0', '--query-gpu=temperature.gpu', '--format=csv,noheader'], capture_output=True, text=True))
        return int(result.stdout)
    except:
        return min_temperature

def computeFanSpeed(current_temperature, min_temperature_range, max_temperature_range, factor, min_fan_speed,
                    max_fan_speed):
    if current_temperature <= min_temperature_range:
        return int(min_fan_speed)
    if current_temperature >= max_temperature_range:
        return int(max_fan_speed)
    speed = factor * (current_temperature - min_temperature_range) ** exp + min_fan_speed
    if speed <= min_fan_speed:
        return int(min_fan_speed)
    if speed >= max_fan_speed:
        return int(max_fan_speed)
    return int(speed)


def getCurrentTemperature(device, sensor):
    hwmon_path = "/sys/class/hwmon"
    # device_pattern = re.compile("(device.*?)/hwmon.*")
    hwmon_list = os.listdir(hwmon_path)
    current_temperature = min_temperature
    for hwmon in hwmon_list:
        hwmon_device_dir = os.path.join(hwmon_path, hwmon)
        hwmon_device_name = os.path.join(hwmon_device_dir, "name")
        with open(hwmon_device_name) as file_name:
            name = file_name.readline().rstrip("\r\n")
            if name == device:
                hwmon_device_temp = os.path.join(hwmon_device_dir, sensor)
                with open(hwmon_device_temp) as file_temp:
                    current_temperature = int(file_temp.readline().rstrip("\r\n")) * .001
                    file_temp.close()
            file_name.close()
    return current_temperature


def getAttribute(attribute_path):
    with open(attribute_path) as attribute:
        return attribute.readline().rstrip("\r\n")


def getCurrentGpuTemperature(device, id, sensor):
    hwmon_path = "/sys/class/hwmon"
    # device_pattern = re.compile("(device.*?)/hwmon.*")
    hwmon_list = os.listdir(hwmon_path)
    current_temperature = 0
    for hwmon in hwmon_list:
        hwmon_device_dir = os.path.join(hwmon_path, hwmon)
        hwmon_device_name = os.path.join(hwmon_device_dir, "name")
        hwmon_unique_id = os.path.join(hwmon_device_dir, "device", "unique_id")
        name = getAttribute(hwmon_device_name)
        if name == device:
            unique_id = getAttribute(hwmon_unique_id)
            if id == unique_id:
                hwmon_device_temp = os.path.join(hwmon_device_dir, sensor)
                file_temp = getAttribute(hwmon_device_temp)
                current_temperature = int(file_temp) * .001
    return current_temperature


def get_fan_speed_or_default(fan_speed=None, default_fan_speed=min_fan_speed):
    return fan_speed if fan_speed is not None else default_fan_speed


current_fan_1_speed = get_fan_speed_or_default()
current_fan_2_speed = get_fan_speed_or_default(default_fan_speed=50)
current_fan_3_speed = get_fan_speed_or_default()
current_fan_4_speed = get_fan_speed_or_default()
current_fan_5_speed = get_fan_speed_or_default(default_fan_speed=50)
current_fan_6_speed = get_fan_speed_or_default(default_fan_speed=50)
current_fan_7_speed = get_fan_speed_or_default(default_fan_speed=50)


def set_fan_speed(fan_1_speed=None, fan_2_speed=None, fan_3_speed=None, fan_4_speed=None, fan_5_speed=None,
                  fan_6_speed=None, fan_7_speed=None):
    global current_fan_1_speed
    global current_fan_2_speed
    global current_fan_3_speed
    global current_fan_4_speed
    global current_fan_5_speed
    global current_fan_6_speed
    global current_fan_7_speed
    current_fan_1_speed = get_fan_speed_or_default(fan_1_speed, current_fan_1_speed)
    current_fan_2_speed = get_fan_speed_or_default(fan_2_speed, current_fan_2_speed)
    current_fan_3_speed = get_fan_speed_or_default(fan_3_speed, current_fan_3_speed)
    current_fan_4_speed = get_fan_speed_or_default(fan_4_speed, current_fan_4_speed)
    current_fan_5_speed = get_fan_speed_or_default(fan_5_speed, current_fan_5_speed)
    current_fan_6_speed = get_fan_speed_or_default(fan_6_speed, current_fan_6_speed)
    current_fan_7_speed = get_fan_speed_or_default(fan_7_speed, current_fan_7_speed)
    subprocess.call(["/usr/bin/ipmitool", "raw", "0x3a", "0xd6", "0x32", f"{hex(current_fan_2_speed)}",
                     f"{hex(current_fan_3_speed)}",
                     f"{hex(current_fan_4_speed)}", f"{hex(current_fan_5_speed)}", f"{hex(current_fan_6_speed)}",
                     f"{hex(current_fan_7_speed)}", "0x32", "0x32", "0x32", "0x32",
                     "0x32", "0x32", "0x32", "0x32", "0x32"])


initial_gpu_temperature = getCurrentGpuTemperature(amd_gpu, gpu_1_id, gpu_temp_sensor)
initial_gpu_2_temperature = getCurrentGpuTemperature(amd_gpu, gpu_2_id, gpu_temp_sensor)
# initial_gpu_temperature, initial_gpu_2_temperature = getCurrentGpuTemperatures(amd_gpu, gpu_temp_sensor)
initial_cpu_temperature = getCurrentTemperature(amd_cpu, cpu_temp_sensor)
gpu_temperatures = [initial_gpu_temperature for _ in range(10)]
gpu_2_temperatures = [initial_gpu_2_temperature for _ in range(10)]
cpu_temperatures = [initial_cpu_temperature for _ in range(10)]
previous_gpu_temperature = initial_gpu_temperature
previous_gpu_2_temperature = initial_gpu_2_temperature
previous_cpu_temperature = initial_cpu_temperature
desired_fan_speed_3 = computeFanSpeed(initial_gpu_temperature, min_temperature, max_temperature, gpu_factor,
                                      min_fan_speed, max_fan_speed)
desired_fan_speed_4 = int(desired_fan_speed_3 * .9)
desired_fan_speed_7 = computeFanSpeed(initial_gpu_2_temperature, min_temperature, max_temperature, gpu_factor,
                                      min_fan_speed, max_fan_speed)

set_fan_speed(fan_3_speed=desired_fan_speed_3, fan_4_speed=desired_fan_speed_4, fan_2_speed=min_cpu_fan_speed, fan_7_speed=desired_fan_speed_7)

while True:
    current_gpu_temperature = getCurrentGpuTemperature(amd_gpu, gpu_1_id, gpu_temp_sensor)
    current_gpu_2_temperature = getCurrentGpuTemperature(amd_gpu, gpu_2_id, gpu_temp_sensor)
    # current_gpu_temperature, current_gpu_2_temperature = getCurrentGpuTemperatures(amd_gpu, gpu_temp_sensor)

    gpu_temperatures.pop(0)
    gpu_temperatures.append(current_gpu_temperature)

    gpu_2_temperatures.pop(0)
    gpu_2_temperatures.append(current_gpu_2_temperature)

    current_cpu_temperature = getCurrentTemperature(amd_cpu, cpu_temp_sensor)
    cpu_temperatures.pop(0)
    cpu_temperatures.append(current_cpu_temperature)

    # smooth out fluctuations
    average_gpu_temperature = sum(gpu_temperatures) / len(gpu_temperatures)
    average_gpu_2_temperature = sum(gpu_2_temperatures) / len(gpu_2_temperatures)
    average_cpu_temperature = sum(cpu_temperatures) / len(cpu_temperatures)

    # if abs(previous_temperature - average_temperature) > 1.5:
    previous_gpu_temperature = average_gpu_temperature
    previous_gpu_2_temperature = average_gpu_2_temperature
    previous_cpu_temperature = average_cpu_temperature

    # compute the max speed of 1 GPU fan
    # set other GPU fan to 90% of first fan to reduce resonating
    desired_fan_speed_3 = computeFanSpeed(average_gpu_temperature, min_temperature, max_temperature, gpu_factor,
                                          min_fan_speed, max_fan_speed)
    desired_fan_speed_4 = int(
        desired_fan_speed_3 * .9)  # desired_fan_speed_1 - 10  # int(computeFanSpeed(average_temperature, min_temperature_2, max_temperature_2))

    desired_fan_speed_7 = computeFanSpeed(average_gpu_2_temperature, min_temperature, max_temperature, gpu_factor,
                                          min_fan_speed, max_fan_speed)

    # set the case fans to the maximum of either:
    # 1. computed cpu fan speed
    # 2. second gpu fan speed
    computed_fan_speed = computeFanSpeed(average_cpu_temperature, min_cpu_temperature, max_cpu_temperature, cpu_factor,
                                         min_cpu_fan_speed, max_cpu_fan_speed)

    desired_fan_speed_case = max(desired_fan_speed_4, desired_fan_speed_7,
                                 computed_fan_speed) if max(desired_fan_speed_4, desired_fan_speed_7) > min_fan_speed * 1.1 else computed_fan_speed
    # only adjust if delta exceeds fluctuation threshold
    if current_fan_3_speed != desired_fan_speed_3 or current_fan_2_speed != desired_fan_speed_case or current_fan_7_speed != desired_fan_speed_7:
        # sudo ipmitool raw 0x3a 0xd6 0x64 0x64 0x32 0x32 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64 0x64
        set_fan_speed(fan_3_speed=desired_fan_speed_3, fan_4_speed=desired_fan_speed_4,
                      fan_2_speed=min_cpu_fan_speed, fan_7_speed=desired_fan_speed_7)

    time.sleep(2)
