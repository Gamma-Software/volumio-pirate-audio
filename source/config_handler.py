def read_config(config_file) -> dict:
    config = configparser.ConfigParser()
    config.read('/data/configuration/audio_interface/pirate_audio_dac/config.ini')
    return config