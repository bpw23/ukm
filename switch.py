from functions import get_config


class Switch(object):
    def __init__(self, switch_id):
        self.id = switch_id
        self.config = get_config()['devices'][self.id]
        self.ip = self.config['IP']
        self.name = self.config['NAME']
        self.project_id = self.config['PROJECT_ID']
        self.design_id = self.config['DESIGN_ID']
        self.group_address_values = {}

        # switch sensors
        self.proximity_sensor = False
        self.addon_motion_sensor = False
        self.addon_voc_sensor = False
        self.addon_in2 = False
        self.addon_co2 = False
        self.addon_humidity = False
        self.addon_temperature = False
        self.light_sensor = False

        # sensor values
        self.light_brigthness = 0
        self.temperature = 0
        self.humidity = 0

        # switch items
        self.display_active = False
        self.audio_active = False
        self.page_active = 0
        self.nr_pages = 0
        self.intro_active = False
        self.device_error = False


