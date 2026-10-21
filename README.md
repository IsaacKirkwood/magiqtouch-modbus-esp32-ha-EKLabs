# Home Assistant Integration for the MagiqTouch Modbus ESP32 Interface

## Hardware requirements

An ESP32 controller exposing the MagiqTouch Modbus HTTP API. The original interface project is [mrhteriyaki/magiqtouch-modbus-esp32](https://github.com/mrhteriyaki/magiqtouch-modbus-esp32). This fork also supports controllers reporting `controller_protocol: "magiqcool"` and a `magiqcool_override` status field.

## Installation

Add **this fork** as a custom integration repository in HACS: [IsaacKirkwood/magiqtouch-modbus-esp32-ha-EKLabs](https://github.com/IsaacKirkwood/magiqtouch-modbus-esp32-ha-EKLabs). Install the latest release and restart Home Assistant. For a manual installation, copy `custom_components/magiqtouch_modbus` into your Home Assistant `custom_components` directory and restart Home Assistant.


## Configuration

![config](Images/config.PNG)  

1. Set the base URL of the HVAC ESP32 module, for example `http://192.168.20.112`. The integration reads status from this URL and sends commands to `/command`; do not add `/status` to the URL.
2. Set your zone count.  
3. Tick Evap / Heater modules for your supported setup.  

Home Assistant must be able to reach the ESP32 over the network. The computer running your browser does not need to be on the same VLAN as the ESP32.

### MagIQcool control source

For a MagIQcool controller, the integration adds a **Control source** selector:

- **Wall controller** leaves HVAC control with the wall panel. Zone climate commands from this integration are rejected while this option is selected.
- **Home Assistant** enables HVAC commands from the Zone climate entities.

The selector displays the `magiqcool_override` value reported by the ESP32. MagIQcool firmware can switch back to Home Assistant control when it receives an HVAC command, even `power=off`. Version 1.1.6 prevents climate commands from this integration from reclaiming control after **Wall controller** is selected. Other software sending commands directly to the ESP32 may still change its control source.

### Zone climate controls

Zone 1 supports power, fan, and cooler modes when the configured hardware provides them. Version 1.1.5 keeps numeric fan speeds available while the unit is off, sends commands as plain text, and reports failed commands to Home Assistant. Version 1.1.6 uses MagIQcool requested power and operating state to show **Off** when the unit is idle; the ESP32 may still report `system_power: 1` in that state. Commands refresh the integration's status after they are sent.

If a climate command fails, check the Home Assistant log for `magiqtouch_modbus` errors and read the ESP32's status at its base URL. Useful MagIQcool fields include `magiqcool_override`, `magiqcool_requested_power`, `magiqcool_requested_fan_speed`, `magiqcool_operating_state`, and `hvac_link_healthy`. A successful HTTP response means the ESP32 accepted the command; compare the requested values with the reported fan speed and operating state to confirm that the HVAC unit applied it.

### Recent fixes

| Version | Changes |
| --- | --- |
| 1.1.6 | Prevent Zone climate commands while Wall controller is selected; correct the idle MagIQcool climate state. |
| 1.1.5 | Improve climate command errors and status refresh; keep fan speed controls available while off. |
| 1.1.4 | Improve HTTP polling and command timeout handling during intermittent ESP32 responses. |

Dashboard display:  
![dash](Images/dash.PNG)

Details showing fan speed selection and option to use temperature mode:  
![z1detail](Images/z1detail.PNG)  

![z1detailfan](Images/fan.png)

Dashboard with Logbook:
![dashboardwithlog](Images/Dashboard_Log.PNG)
