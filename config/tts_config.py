import json

tts_config_file = open("./config/tts-config.json", "r")
tts_config: list[dict] = json.load(tts_config_file)
tts_config_file.close()
