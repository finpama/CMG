import json


def read_configFile(configType:str, configKey: str | None = None):
    
    with open('./api_config.json', 'r') as file:
        config = json.loads(file.read())
        
        if configKey == None:
            return config[configType]
        else:
            return config[configType][configKey]
    
    