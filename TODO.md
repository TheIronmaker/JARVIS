# Core
## Module Loading (Very important)
importlib for loading modules, instead of storing each class in the manager class.
ID system for devices / modules instead of naming (or importlib - look into this)

## Settings Loading
Look into `pydantic`
Define a scheme class and validation step
Eliminate need for NodeManager with better loading services

## Fingers
Redo calculations for finger angles with a dedicated function for a single finger

Render inverse kinematics in new graph

## Logging:
Add some way to send error message only once. Use ID or some tracking method. Have cool-down setting for repeating once per timeframe.
Logging should have actual log file
Logging should have verbose version
Logging should have calling setting for verbose level/where the message goes. To screen log, just text, or only internal logs (again, what level of internal logs?)

# Application
## App Core: UI
Dynamic GUI constructor
Example format:
``` JSON
{
  "layout_name": "Research_Dashboard",
  "root": {
    "type": "split_v",
    "ratio": 0.7,
    "top": { "slot": "main_viewport" },
    "bottom": {
        "type": "split_h",
        "left": { "slot": "sidebar_controls" },
        "right": { "slot": "console_output" }
    }
  }
}
```
