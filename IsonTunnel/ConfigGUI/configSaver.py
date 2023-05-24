import yaml
    
class Common:
    def __init__(self) :
        self.path = 'configure/common.yaml'
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

    with open('configure/common.yaml', 'w') as f:
        yaml.dump(common_config, f, default_flow_style=False)
    
    with open(f'configure/config_{mode}.yaml', 'w') as f:
        yaml.dump(else_config, f, default_flow_style=False)

# class Event:
#     def __init__(self) :
#         self.path = 'configure/config_event.yaml'
#         with open(self.path, errors='ignore', encoding='utf-8') as f:
#             s = f.read()  # string
#             self.config = yaml.safe_load(s)
#         self.keys = self.config.keys()

#     def get_keys(self):
#         return self.keys

# def save_config(data, mode='common'):
#     """

#     Args:
#         data (_type_): _description_
#         mode (list, optional): _description_. Defaults to [].
#     """
#     if mode == 'common':
#         print('NOT IMPLEMENTED')
#     elif mode == 'event':
#         save_event_config(data)
#     elif mode == 'detect':
#         save_detect_config(data)
#     else:
#         print('NOT IMPLEMENTED')
        
    

# def save_event_config(data):
#     common = Common()
#     common_keys = common.get_keys()
    
#     common_config = {}
#     else_config = {}
    
#     for k, v in data.items():
#         if k in common_keys:
#             common_config[k] = v
#         else:
#             else_config[k] = v

#     common_config = common.rearrange(common_config)

#     with open('configure/common_test.yaml', 'w') as f:
#         yaml.dump(common_config, f)
    
#     with open('configure/config_event_test.yaml', 'w') as f:
#         yaml.dump(else_config, f)

# def save_detect_config(data):
#     common = Common()
#     common_keys = common.get_keys()
    
#     common_config = {}
#     else_config = {}
    
#     for k, v in data.items():
#         if k in common_keys:
#             common_config[k] = v
#         else:
#             else_config[k] = v

#     common_config = common.rearrange(common_config)

#     with open('configure/common_test.yaml', 'w') as f:
#         yaml.dump(common_config, f)
    
#     with open('configure/config_detect_test.yaml', 'w') as f:
#         yaml.dump(else_config, f)