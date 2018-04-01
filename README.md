# home_temp_mon
## TODO
* Actually split into other files
* Add script to check scheduler and add if not
* Log file: cleanup evenually? Not with admin? (Add this to logging library..)
* add real link to logging library

## Setup
Currently running it with supervisor. Config is super simple.

Also, need to put the adafruit secret in file: `adakey.secret`

Also needs my log library, should add that somewhere...

For startup
https://learn.adafruit.com/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/ds18b20

sudo pip install adafruit-io
sudo touch /var/log/temp_monitor.log
sudo touch /var/log/standard.log
and chmod both to 666
