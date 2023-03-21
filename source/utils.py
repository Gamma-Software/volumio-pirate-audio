import os
import json
from source import SIMULATOR


def read_config(config_file) -> dict:
    with open(config_file, 'r') as filestream:
        data = filestream.read()
    return json.loads(data)


config_root_path = "/data/configuration/" if not SIMULATOR else ""
plugin_root_path = "/data/plugins/system_hardware/" if not SIMULATOR else ""

# read json file (plugin values)
config_file = config_root_path + ('system_hardware/pirateaudio/config.json' if not SIMULATOR else 'config.json')
CONFIG_DATA = read_config(config_file)

# read json file (volumio language)
lang_file = config_root_path + ('miscellanea/appearance/config.json' if not SIMULATOR else 'misc_config.json')
language_code = read_config(lang_file)['language_code']['value']

messages_data_path = ''.join([(plugin_root_path + 'pirateaudio/' if not SIMULATOR else '') + 'i18n/strings_', language_code, '.json'])
if not os.path.exists(messages_data_path):  # fallback to en as default language
    messages_data_path = (plugin_root_path + 'pirateaudio/' if not SIMULATOR else '') + 'i18n/strings_en.json'

# read json file (language file for translation)
MESSAGES_DATA = read_config(messages_data_path)
