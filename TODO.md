# Application

## Hand Tracking 🔲 ✅
General Purpose
---
🔲 Average of main hand points for orientation base

## Fingers
🔲 Redo calculations for finger angles with a dedicated function for a single finger
🔲 Render inverse kinematics in new graph

## Settings
Separate Gui settings from system settings
Rename to module_settings.json
Create main_settings.json if needed

## Logging:
Add some way to send error message only once. Use ID or some tracking method. Have cool-down setting for repeating once per timeframe.
Logging should have actual log file
Logging should have verbose version
Logging should have calling setting for verbose level/where the message goes. To screen log, just text, or only internal logs (again, what level of internal logs?)

Add state machine for module life-cycles