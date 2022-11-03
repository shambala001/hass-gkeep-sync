# HASS Google Keep (Sync)

Custom component for [Home Assistant](https://home-assistant.io) to enable adding to and updating lists on [Google Keep](https://keep.google.com).

## Installation

Add the `gkeep` folder and its contents to the `custom_components` folder in your Home Assistant configuration directory, and add the `gkeep` component to your `configuration.yaml` file.

### Example `configuration.yaml` entry

```yaml
gkeep_sync:
  username: 'this_is_my_username@gmail.com'
  password: 'this_is_my_Google_App_password'
  list_name: 'Food Shopping'
```

`list_name` is an optional configuration key that sets a default name for the Keep list to update.

### Dependencies

This component relies on [gkeepapi](https://github.com/kiwiz/gkeepapi), an unofficial client for the Google Keep API.

## Usage

The original intended use of this component was to restore the capability of Google Assistant to add items to Google Keep lists.

### Home Assistant service

With this custom component loaded, a service called `gkeep.add_to_list` is available.

#### Add to List

This service call has two data inputs: `name` and `items`, where `name` is the name of the Google Keep list to update, and `items` is a either a list or string of items to add to the list.
A string input for `items` is parsed for multiple items separated by 'and' and/or commas.

Here is an example of using the service in an automation to add batteries for smart home devices to a list named "Home Supplies":
```yaml
automation:
  - alias: Low Battery Notification
    trigger:
      - platform: numeric_state
        entity_id:
        - sensor.front_door_battery
        - sensor.hallway_smoke_co_alarm_battery
        - sensor.bedroom_sensor_battery
        below: 20
    action:
      service: gkeep.add_to_list
      data:
        name: 'Home Supplies'
        items: 'Batteries for {{ trigger.to_state.name }}.'
```
