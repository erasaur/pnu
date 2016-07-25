from os import environ, path
import json

class Configurable:
    def __init__(self, config_path=None):
        if config_path is None:
            self.config_path = environ.get(
                'PNU_CONFIG',
                path.join(path.dirname(__file__), 'etc/config.json'),
            )
        else:
            self.config_path = config_path

    def return_config(self):
        with open(self.config_path, 'r') as f:
            return json.load(f)

class Config(Configurable):
    """ returns public data utilized by pnu """

    def __init__(self):
        super().__init__('etc/config.json')

    def load_config(self):
        return super().return_config()

class PrivateConfig(Configurable):
    """ return sensitive data utilized by pnu """

    def __init__(self):
        super().__init__('private/config.json')

    def load_config(self):
        return super().return_config()

pub_config = Config().load_config()
private_config = PrivateConfig().load_config()
