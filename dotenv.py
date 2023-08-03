import os
from typing import Dict, Optional


class DotENV():
    def __init__(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        env_filepath = os.path.join(this_dir, '.env')
        self.env_vars = self.read_env_file(env_filepath)
        # print(".env loaded")


    def read_env_file(self, file_path) -> Optional[Dict[str, str]]:
        if not os.path.isfile(file_path):
            return None

        env_vars = {}

        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()

        return env_vars

    def get(self, key, default='') -> str:
        if self.env_vars == None:
            return default
        return self.env_vars.get(key) or default

    def is_true(self, key: str):
        if self.get(key).lower == 'true':
            return True
        return False
