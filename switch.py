from functions import get_config


class Switch(object):
    def __init__(self, switch_id):
        self.id = switch_id
        self.config = get_config()['devices'][self.id]
        self.ip = self.config['IP']
        self.name = self.config['NAME']
        self.project_id = self.config['PROJECT_ID']
        self.design_id = self.config['DESIGN_ID']

        # switch sensors
        self.proximity_sensor = False
        self.motion_sensor = False
        self.light_sensor = False
        self.temperature = 0
        self.humidity = 0

        # switch items
        self.display_active = False
        self.audio_active = False
        self.page_active = 0
        self.nr_pages = 0


