import os
from .local import SETTINGS as default_settings
from .prod import SETTINGS


BASE_DIR = os.path.dirname(os.path.realpath(os.path.dirname(__file__) + "/.."))

default_settings.update(SETTINGS)
SETTINGS = default_settings
