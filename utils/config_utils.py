# -- coding: utf-8 --

import yaml


def load_config(config_path):
    with open(config_path, encoding='utf8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)
