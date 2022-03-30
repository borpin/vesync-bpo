# VeSync custom-integration for Home-Assistant

This is a vesync integration that can be installed while waiting for main integration to be updated

Install to a folder called `vesync2` in your `custom-integrations` folder and restart HA. Then Add a new integration and you will see the `vesync2` integration listed.

The current HA Core PR this is pulled from is https://github.com/home-assistant/core/pull/62907

Key changes are that it now supports all devices and models found in the core Python Library https://github.com/webdjoe/pyvesync

as at 30/03/22 there are still some wrinkles to iron out.
