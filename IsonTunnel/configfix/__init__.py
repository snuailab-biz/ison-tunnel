from IsonTunnel.utils import get_cfg

COMMON_CFG = get_cfg('IsonTunnel/configure/common.yaml')
DETECT_CFG = get_cfg('IsonTunnel/configure/common.yaml', 'IsonTunnel/configure/config_detect.yaml')
EVENT_CFG = get_cfg('IsonTunnel/configure/common.yaml', 'IsonTunnel/configure/config_event.yaml')
RTSP_CFG = get_cfg('IsonTunnel/configure/common.yaml', 'IsonTunnel/configure/config_rtsp.yaml')
SIMULATOR_CFG = get_cfg('IsonTunnel/configure/common.yaml', 'IsonTunnel/configure/config_simulator.yaml')
STITCH_CFG = get_cfg('IsonTunnel/configure/common.yaml', 'IsonTunnel/configure/config_stitch.yaml')
