from IsonTunnel import CONFIG_ROOT
from IsonTunnel.utils import get_cfg, IsonLogger

EVENTER_CFG = get_cfg( CONFIG_ROOT / 'common.yaml',  CONFIG_ROOT / 'config_event.yaml')
LOGGER = IsonLogger("Eventer")

__all__ = 'app_detect', "CONFIG_ROOT", "CFG", "LOGGER"