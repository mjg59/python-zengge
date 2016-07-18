Python control for Zengge-style LED bulbs
=========================================

A simple Python API for controlling LED bulbs compatible with the [Zengge](http://www.enledcontroller.com/) protocol. This covers a wide range of bulbs. This code makes use of the PyBT2 branch of Mike Ryan's [PyBT](http://github.com/mikeryan/PyBT)

Example use
-----------

This will connect and set the bulb to full red, no green and no blue.
```
import zengge

bulb = zengge.zengge("00:21:4d:00:00:01")
bulb.connect()
bulb.set_rgb(0xff, 0x00, 0x00)
```

This will set the intensity of the warm white LEDs to 50%
```
bulb.set_white(0x80)
```

This will turn on the white LEDs at the same time as the colour LEDs (note that this may result in a small quantity of flickering during colour changes)
```
bulb.set_rgbw(0xff, 0x80, 0x10, 0xff)
```

This will turn the bulb on
```
bulb.on()
```

This will turn the bulb off
```
bulb.off()
```

Get a list of the current red, green and blue values
```
(red, green, blue) = bulb.get_colour()
```

Get the current white intensity
```
white = bulb.get_white()
```

Get aboolean describing whether the bulb is on or off
```
on = bulb.get_on()
```

Notes
-----

Note that this has been written against a specific bulb, and may misbehave on some other bulbs that speak a similar protocol. Please get in touch if you have a bulb that partially works with this code.

The set_rgbw() mode appears to bypass a great deal of the bulb's normal functionality - for instance, turning the bulb off and then on will not restore the state programmed by set_rgbw(). Further, calling set_rgbw() while the bulb is still fading up from an on() command will not have the desired effect.