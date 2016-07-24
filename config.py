from os import environ, path
import json


class Configurable:
    """ returns public data utilized by pnu """

    @staticmethod
    def load_config(config_path='etc/config.json'):
        if config_path is None:
            config_path = environ.get(
                'PNU_CONFIG',
                path.join(path.dirname(__file__), 'etc/config.json'),
            )

        with open(config_path, 'r') as f:
            return json.load(f)


class PrivateConfig(Configurable):
    """ return sensitive data utilized by pnu """

    @staticmethod
    def load_private(config_path='private/config.json'):
        return self.load_confnig(config_path)

