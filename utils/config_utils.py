# -- coding: utf-8 --

import yaml


def load_config(config_path):
    f = open(config_path)
    return yaml.load(f, Loader=yaml.FullLoader)
