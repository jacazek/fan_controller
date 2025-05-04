import os

def getAttribute(attribute_path):
    with open(attribute_path) as attribute:
        return attribute.readline().rstrip("\r\n")

def getCurrentTemperature(device, id, sensor):
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

print(getCurrentTemperature("amdgpu", "f4ae5c2ae0aec465", "temp1_input"))
print(getCurrentTemperature("amdgpu", "4d91a42a85aa9594", "temp1_input"))