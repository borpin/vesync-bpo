Forked from https://github.com/borpin/vesync-bpo

# VeSync custom-integration for Home-Assistant

This is a vesync integration that can be installed while waiting for main HA integration to be updated

Install to a folder called `vesync2` in your `custom-integrations` folder and restart HA. Then Add a new integration and you will see the `vesync2` integration listed.

The current HA Core PR this is pulled from is https://github.com/home-assistant/core/pull/62907
Included 2 binary_sensors from https://github.com/alexanv1/core/tree/vesync_humidifier_support/homeassistant/components/vesync

Key changes are that it now supports all devices and models found in the core Python Library https://github.com/webdjoe/pyvesync

as at 30/03/22 there are still some wrinkles to iron out.

## Sample script to test what the Library is saying about your devices

```python
from pyvesync import VeSync
#from pyvesync.vesyncfan import model_features

# TIME_ZONE and Debug are optional
manager = VeSync("EMAIL", "PASSWORD", "TIME_ZONE", debug=True)
manager.login()

# Get/Update Devices from server - populate device lists
manager.update()

# Display fan devices found
for device in manager.fans:
  device.display()

# Other bits I did to test stuff

#my_fan = manager.fans[0]
#print (manager.fans[0])
#my_fan.set_humidity(40)
#fan_features = model_features(my_fan.device_type)
#print(model_features(my_fan.device_type)["module"])
#print(my_fan.humidity)
#my_fan.display()
```
