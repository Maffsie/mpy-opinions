# mpy-opinions
the opinions library for micropython.

# opinions?
opinions is the name i've given to libraries i write which enforce (or make easier) the implementation of my opinions regarding software development.

# okay, but, opinions?
look. maybe this will be the first thing you've seen on github that describes itself as opinionated and isn't deliberately the worst thing you've ever fucking seen. i have ways i like to do things and i promise i'm a sane person who writes functional software.

# contents
i will forget to update this, but here's the initial set of what's in here:

## opinions.I2CPeripheral
Shim class intended to handle the boring or boilerplate parts of I2C devices in micropython.

### usage
Inherit from I2CPeripheral and define your initialisation code in `def init(*args, **kwargs)`. You can of course use super() instead but i fuckin hate having to google every time how to use super() and i don't remember what the deal is with a difference in arguments, so instead you should use `init()` to accept and handle your extra args.

Define your i2c device's default address as `default_address` in the class itself, and I2CPeripheral will use it automatically if an address isn't supplied during `__init__(bus, address)`.

You should probably supply a `bus` value, if for no other reason than it's insane to try and have the library auto-setup I2C when there're so many pinouts. for reference's sake:
* micropython's default is peripheral=0, sda=8, scl=9
* pimoroni's pico breakout garden base uses peripheral=0, sda=4, scl=5
* pimoroni's pico explorer base uses peripheral=0, sda=20, scl=21
* pimoroni's automation2040, badger2040, enviro, keybow2040, inky frame 5.7, inventor2040 and tufty2040 boards, as well as the pico rgb keypad base, use the same pinmap as the pico breakout garden base.
* pimoroni's interstate75, motor2040, plasma2040 and servo2040 boards use the same pinmap as the pico explorer base.
