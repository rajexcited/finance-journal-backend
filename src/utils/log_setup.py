import logging
import logging.handlers as handlers
from pathlib import Path
from datetime import datetime

today = datetime.today().strftime("%d_%m_%Y")

level = logging.DEBUG
log_filename = f"finance_app_{today}.log"


log_dir = Path.cwd()/"../logs"
log_dir.mkdir(exist_ok=True, parents=True)
log_path = log_dir.joinpath(log_filename)

logger = logging.getLogger()
logger.setLevel(level)

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-6s| %(name)s:%(lineno)s | %(funcName)s() |  %(message)s")

streamhandler = logging.StreamHandler()
streamhandler.setFormatter(formatter)
logger.addHandler(streamhandler)

filehandler = logging.FileHandler(log_path)
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

timehandler = handlers.TimedRotatingFileHandler(
    log_path, when="H", interval=12, backupCount=10)
logger.addHandler(timehandler)

rotatehandler = handlers.RotatingFileHandler(
    log_path, maxBytes=2*1024*1024, backupCount=10)
logger.addHandler(rotatehandler)
