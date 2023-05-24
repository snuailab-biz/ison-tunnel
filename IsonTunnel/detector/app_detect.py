import sys
from _thread import start_new_thread
from IsonTunnel.detector.config import DEFAULT_CFG, logger
from IsonAI import IsonPredictor, ServerIson, ServerHandler, image_queue, unity_queue


class IsonMain:
    def __init__(self, config):
        model = config.detect_model
        source = config.camera_url
        imgsz = config.detect_imgsz
        args = dict(model=model, source=source, imgsz=imgsz)
        self.predictor = IsonPredictor(overrides=args)
        self.server = ServerIson((config.detect_ip, config.detect_port), ServerHandler)

    def run_detector(self):
        start_new_thread(self.predictor.stream_inference, (image_queue, unity_queue,))

    def run_server(self):
        try:
            logger.info("Detector Sever Start")
            self.server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Detector Sever Exit")
            self.server.shutdown()
            self.server.server_close()
    
    def run(self):
        logger.info("Run Detector")
        self.run_detector()
        logger.info("Run Server")
        self.run_server()
    

def run():
    try:
        main = IsonMain(config=DEFAULT_CFG)
        main.run()
    except Exception as e:
        logger.exception(e)
        sys.exit(1)

if __name__ == '__main__':
    run()