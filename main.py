import subprocess
import logging
from datetime import datetime
import os
import sys

log_dir = os.path.join(os.path.dirname(__file__), 'ouput.logs')
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = os.path.join(log_dir, f"output_{timestamp}.log")  # or just "output.log" to overwrite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)  # also show in terminal
    ]
)
# logging.info("🚀 main.py is starting...")

logging.info("running public_info_banjir_waterlevel.py")
subprocess.run(["python", "collector/script/public_info_banjir_waterlevel.py"])

logging.info("running public_info_banjir_rainfall.py")
subprocess.run(["python", "collector/script/public_info_banjir_rainfall.py"])
