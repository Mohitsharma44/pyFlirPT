# pyflir
Python wrapper for controlling the FLIR E Series Pan and Tilt devices.

> Note:
> - Remember to add the path where you clone this repo to your `PATH` global variable. I don't use relative imports.

## Usage:
#### Using joystick
**Ipython:**
```
import joystick
js = joystick.JoystickControl()
js.auth()
js.select_joystick(0)
```

#### Using keyboard
**Ipython**
```
kctrl = keyboard.KeyboardController("192.168.1.50", 4000)
kctrl.pan(100)
kctrl.tilt(200)
```

**Using a script**
Refer the `samples` directory

Enjoy panning and tilting..
