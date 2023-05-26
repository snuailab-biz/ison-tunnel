from IsonTunnel import CONFIG_ROOT
from IsonTunnel.utils import get_cfg, IsonLogger

STITCH_CFG = get_cfg( CONFIG_ROOT / 'common.yaml', CONFIG_ROOT / 'config_stitch.yaml')
LOGGER = IsonLogger("Stitch")

__all__ = 'app_detect', "CONFIG_ROOT", "STITCH_CFG", "LOGGER"