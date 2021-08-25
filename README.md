# ukm
u::lux - knx - middleware

This is absolut alpha stage!

I'm trying to implement a middleware for the u::lux switch (u-lux.com), to transform the commands from the switch into KNX commands and vice versa.
Yes, there are u::Lux KNX switches, but they have not the same amount of features than the network types!
You can only use the pre-configured design and pages. And that is the main point, why i'm doing this.

Ideas for this middleware:
- generate switch state json for use in other programs, or implement full rest api
- video and audio will be an optional feature!
- u::lux switches are configured via the u::lux config
- Webinterface for switch configuration
- import of KNX ETS files from a project (for the addresses)
- import of ulux configuration (actors)
