from IsonTunnel import CONFIG_ROOT
from IsonTunnel.utils import get_cfg, IsonLogger

STREAM_CFG = get_cfg(CONFIG_ROOT / 'common.yaml', CONFIG_ROOT / 'config_rtsp.yaml')
LOGGER = IsonLogger("simulator_stream")

__all__ = 'app_detect', "CONFIG_ROOT", "STREAM_CFG", "LOGGER"