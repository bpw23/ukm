# ukm
u::lux - knx - middleware

This is absolut alpha stage!

I'm trying to implement a middleware for the u::lux switch (u-lux.com), to transform the commands from the switch into KNX commands and vice versa.
Yes, there are u::Lux KNX switches, but they have not the same amount of features than the network types!
You can only use the pre-configured design and pages. And that is the main point, why i'm doing this.
  
The configuration of the u::Lux switches is done via their own software.
The communication configuration between KNX + json and the u::Lux switches is done via a config file
___
## Configuration
This is done via a config.json file (not included in the uploaded fiels here)
Since the json 'styling' is still WIP, i will later upload the config.
___
Working:
- [X] Init the switch
- [X] Write date and time to switch
- [X] Write values for an actor to switch, from KNX or a JSON source
- [X] Read out state flags
- [X] set a page on a switch
___
Ideas that i hope to implement:
- [ ] send values to KNX
- [ ] send state flags to KNX
- [ ] change audio volume (lower volume at night,...)
- [ ] play local saved sound (e.g. for a door bell, warning sound, ...)
- [ ] to sync the clock of the switches, the time must be send every hour
- [ ] set the control flags
- [ ] de/activate the display
- [ ] send text to the switch (e.g. for showing a Music interpret or a station name, ...)
- [ ] generate switch state json for use in other programs
- [ ] show video or still image from a Doorbird video door station
- [ ] Webinterface for switch configuration
  - [ ] import of KNX ETS files from a project (for the addresses)
  - [ ] import of ulux configuration (actors)

Cool, but complex features that will never be integrated:
- [ ] audio between 2 switches
- [ ] audio to a doorbird station
- [ ] implement full rest api
