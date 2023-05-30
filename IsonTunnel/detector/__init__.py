from IsonTunnel.configure import CONFIG_ROOT
from IsonTunnel.utils import get_cfg, IsonLogger

DETECTOR_CFG = get_cfg( CONFIG_ROOT / 'common.yaml', CONFIG_ROOT / 'config_detect.yaml')
LOGGER = IsonLogger("detector")

__all__ = 'app_detect', "CONFIG_ROOT", "CFG", "LOGGER"