# Application
## app_core
Boot loader that checks for if the selected "build.json" works. Ability to view and select different builds from the boot loader, and then it loads them with the ability to set the default build.

Layout orchestrator + layout build.json for placement of views and other types. it handles the placement of everything into the application, but not the creation of those views etc. itself. It's the glue.a

# Core
importlib for loading modules, instead of storing each class in the manager class.
ID system for devices / modules instead of naming (or importlib - look into this)

## Settings Loading
Look into `pydantic`
Define a scheme class and validation step

## Sub-Pub
Could use a thread pool instead of callback execution

## Hand Tracking
General Purpose
---
Average of main hand points for orientation base

## Fingers
Redo calculations for finger angles with a dedicated function for a single finger
Render inverse kinematics in new graph

## Logging:
Add some way to send error message only once. Use ID or some tracking method. Have cool-down setting for repeating once per timeframe.
Logging should have actual log file
Logging should have verbose version
Logging should have calling setting for verbose level/where the message goes. To screen log, just text, or only internal logs (again, what level of internal logs?)