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
- [X] Read json and write values to an actor (WIP)
- [X] Read values from KNX and write to an actor on a switch
- [X] Init the switch
- [X] Write time to switch
- [X] Write values for an actor to switch
- [X] Read out state flags
- [X] set a page on a switch
___
Ideas for this middleware:
- [ ] generate switch state json for use in other programs, or implement full rest api
- [ ] video and audio will be an optional feature!
- [ ] Webinterface for switch configuration
  - [ ] import of KNX ETS files from a project (for the addresses)
  - [ ] import of ulux configuration (actors)
