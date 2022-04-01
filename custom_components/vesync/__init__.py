"""VeSync integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .common import async_process_devices
from .const import (
    DOMAIN,
    SERVICE_UPDATE_DEVS,
    VS_BINARY_SENSORS,
    VS_DISCOVERY,
    VS_FANS,
    VS_HUMIDIFIERS,
    VS_LIGHTS,
    VS_MANAGER,
    VS_NUMBERS,
    VS_SENSORS,
    VS_SWITCHES,
)
from .pyvesync.vesync import VeSync

PLATFORMS = {
    Platform.SWITCH: VS_SWITCHES,
    Platform.FAN: VS_FANS,
    Platform.LIGHT: VS_LIGHTS,
    Platform.SENSOR: VS_SENSORS,
    Platform.HUMIDIFIER: VS_HUMIDIFIERS,
    Platform.NUMBER: VS_NUMBERS,
    Platform.BINARY_SENSOR: VS_BINARY_SENSORS,
}

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.removed(DOMAIN, raise_if_present=False)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up Vesync as config entry."""
    username = config_entry.data[CONF_USERNAME]
    password = config_entry.data[CONF_PASSWORD]

    time_zone = str(hass.config.time_zone)

    manager = VeSync(username, password, time_zone)

    login = await hass.async_add_executor_job(manager.login)

    if not login:
        _LOGGER.error("Unable to login to the VeSync server")
        return False

    device_dict = await async_process_devices(hass, manager)

    forward_setup = hass.config_entries.async_forward_entry_setup

    hass.data[DOMAIN] = {config_entry.entry_id: {}}
    hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER] = manager

    for p, vs_p in PLATFORMS.items():
        hass.data[DOMAIN][config_entry.entry_id][vs_p] = []
        if device_dict[VS_SWITCHES]:
            hass.data[DOMAIN][config_entry.entry_id][vs_p].extend(device_dict[vs_p])
            hass.async_create_task(forward_setup(config_entry, p))

    async def async_new_device_discovery(service: ServiceCall) -> None:
        """Discover if new devices should be added."""
        manager = hass.data[DOMAIN][config_entry.entry_id][VS_MANAGER]
        switches = hass.data[DOMAIN][config_entry.entry_id][VS_SWITCHES]
        fans = hass.data[DOMAIN][config_entry.entry_id][VS_FANS]
        lights = hass.data[DOMAIN][config_entry.entry_id][VS_LIGHTS]
        sensors = hass.data[DOMAIN][config_entry.entry_id][VS_SENSORS]
        humidifiers = hass.data[DOMAIN][config_entry.entry_id][VS_HUMIDIFIERS]
        numbers = hass.data[DOMAIN][config_entry.entry_id][VS_NUMBERS]
        binary_sensors = hass.data[DOMAIN][config_entry.entry_id][VS_BINARY_SENSORS]

        dev_dict = await async_process_devices(hass, manager)
        switch_devs = dev_dict.get(VS_SWITCHES, [])
        fan_devs = dev_dict.get(VS_FANS, [])
        light_devs = dev_dict.get(VS_LIGHTS, [])
        sensor_devs = dev_dict.get(VS_SENSORS, [])
        humidifier_devs = device_dict.get(VS_HUMIDIFIERS, [])
        number_devs = device_dict.get(VS_NUMBERS, [])
        binary_sensor_devs = device_dict.get(VS_BINARY_SENSORS, [])

        switch_set = set(switch_devs)
        new_switches = list(switch_set.difference(switches))
        if new_switches and switches:
            switches.extend(new_switches)
            async_dispatcher_send(hass, VS_DISCOVERY.format(VS_SWITCHES), new_switches)
            return
        if new_switches and not switches:
            switches.extend(new_switches)
            hass.async_create_task(forward_setup(config_entry, Platform.SWITCH))

        fan_set = set(fan_devs)
        new_fans = list(fan_set.difference(fans))
        if new_fans and fans:
            fans.extend(new_fans)
            async_dispatcher_send(hass, VS_DISCOVERY.format(VS_FANS), new_fans)
            return
        if new_fans and not fans:
            fans.extend(new_fans)
            hass.async_create_task(forward_setup(config_entry, Platform.FAN))

        light_set = set(light_devs)
        new_lights = list(light_set.difference(lights))
        if new_lights and lights:
            lights.extend(new_lights)
            async_dispatcher_send(hass, VS_DISCOVERY.format(VS_LIGHTS), new_lights)
            return
        if new_lights and not lights:
            lights.extend(new_lights)
            hass.async_create_task(forward_setup(config_entry, Platform.LIGHT))

        humidifier_set = set(humidifier_devs)
        new_humidifiers = list(humidifier_set.difference(humidifiers))
        if new_humidifiers and humidifiers:
            humidifiers.extend(new_humidifiers)
            async_dispatcher_send(
                hass, VS_DISCOVERY.format(VS_HUMIDIFIERS), new_humidifiers
            )
            return
        if new_humidifiers and not humidifiers:
            humidifiers.extend(new_humidifiers)
            hass.async_create_task(forward_setup(config_entry, Platform.HUMIDIFIER))

        number_set = set(number_devs)
        new_numbers = list(number_set.difference(numbers))
        if new_numbers and numbers:
            numbers.extend(new_numbers)
            async_dispatcher_send(hass, VS_DISCOVERY.format(VS_NUMBERS), new_numbers)
            return
        if new_numbers and not numbers:
            numbers.extend(new_numbers)
            hass.async_create_task(forward_setup(config_entry, Platform.NUMBER))

        sensor_set = set(sensor_devs)
        new_sensors = list(sensor_set.difference(sensors))
        if new_sensors and sensors:
            sensors.extend(new_sensors)
            async_dispatcher_send(hass, VS_DISCOVERY.format(VS_SENSORS), new_sensors)
            return
        if new_sensors and not sensors:
            sensors.extend(new_sensors)
            hass.async_create_task(forward_setup(config_entry, Platform.SENSOR))

        binary_sensor_set = set(binary_sensor_devs)
        new_binary_sensors = list(binary_sensor_set.difference(binary_sensors))
        if new_binary_sensors and binary_sensors:
            binary_sensors.extend(new_binary_sensors)
            async_dispatcher_send(
                hass, VS_DISCOVERY.format(VS_BINARY_SENSORS), new_binary_sensors
            )
            return
        if new_binary_sensors and not binary_sensors:
            binary_sensors.extend(new_binary_sensors)
            hass.async_create_task(forward_setup(config_entry, Platform.BINARY_SENSOR))

    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_DEVS, async_new_device_discovery
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry, list(PLATFORMS.keys())
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
