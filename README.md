# Mouse Flight Control

Mouse Flight Control is designed to provide a intuitive way to control flight in Game. It emulates a joystick's functionality through the mouse.

## Features

- **Mouse Joystick Emulation**: 🖱️ The center of the screen acts as the joystick's midpoint, with screen width representing the X-axis and height the Y-axis. This is a perfect solution for simulating joystick controls with a mouse.
- **Customizable Controls**: 🎮 You can customize key mappings and various options such as cursor display, hint overlays, and use mouse button as joystick button.

## Installation

### Prerequisites
- **vJoy Device Driver**: You need to install the vJoy device driver (recommended version >= 2.1.8). You can download it from [https://github.com/shauleiz/vJoy](https://github.com/shauleiz/vJoy).

### Steps
1. **Download the Software**: 📥 Download the software package from [Releases](https://github.com/Dawson924/MouseFlightControl).
2. **Install vJoy**: Follow the instructions to install the vJoy device driver.
3. **Run the Program**
4. **Setup Controller**: For DCS, drop the MouseFlightControl folder and Export.lua from ./Platform/DCS/ into C:/.../DCS.openbeta/Scripts. In case you already have Export.lua, then add this line of code at the bottom.
```lua
dofile(lfs.writedir()..[[Scripts\MouseFlightControl\MouseFlightControl.lua]]);
```

## Usage

### Starting the Program
- Click the "Start" button to begin using the mouse flight control. 🚀

### Adjusting Sensitivity
- Use the sensitivity slider to adjust the mouse sensitivity. You can set it to a value between 1 - 20. 🔍

### Control Switching
- By default, pressing the `~` key on the keyboard toggles between pausing and resuming control. ⏯️

### Configuration Options
- You can configure various options in the settings menu, including language, controller type, key mappings, and display options. ⚙️

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

## Contact

If you have any questions or feedback, please contact the developer at [bendawson0924@gmail.com](mailto:bendawson0924@gmail.com).

---

Please note that this software is currently in its early stages. While no major issues have been found in tests, it's recommended that you use it with caution. If you encounter any problems or have suggestions for improvement, please feel free to share them. 😊
