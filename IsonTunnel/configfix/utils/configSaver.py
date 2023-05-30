import yaml
from IsonTunnel import CONFIG_ROOT

class Common:
    def __init__(self) :
        self.path = CONFIG_ROOT / 'common.yaml'
        with open(self.path, errors='ignore', encoding='utf-8') as f:
            s = f.read()  # string
            self.config = yaml.safe_load(s)
        self.keys = self.config.keys()

    def get_keys(self):
        return self.keys

    def rearrange(self, data):
        # todo str -> int, str -> list , str -> float 등등의 모든 처리
        return data

def save_config(data, mode='common', allowed_values=['event, detect']):
    common = Common()
    common_keys = common.get_keys()
    
    common_config = {}
    else_config = {}
    
    for k, v in data.items():
        if k in common_keys:
            common_config[k] = v
        else:
            if v.isdigit():
                v = int(v)
            else_config[k] = v
    common_config = common.rearrange(common_config)

    with open(CONFIG_ROOT / 'common.yaml', 'w') as f:
        yaml.dump(common_config, f, default_flow_style=False)
    
    with open(f'{CONFIG_ROOT}/config_{mode}.yaml', 'w') as f:
        yaml.dump(else_config, f, default_flow_style=False)

def check_variable_type(value):
    if isinstance(value, int):
        return int, value
    elif isinstance(value, float):
        return float, value
    elif isinstance(value, str):
        return str, value
    elif isinstance(value, dict):
        return dict, value
    elif isinstance(value, list):
        return list, value
    elif isinstance(value, tuple):
        return tuple, value
    else:
        return None, value