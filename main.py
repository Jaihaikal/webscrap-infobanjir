import subprocess
import logging
from datetime import datetime
import os
import sys

from collector.script.public_info_banjir_rainfall import scrape_rainfall_data
from collector.script.public_info_banjir_waterlevel import scrape_waterlevel_data

# extend function
# pass data to alert.check.py

log_dir = os.path.join(os.path.dirname(__file__), "output.logs")
os.makedirs(log_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d")
log_file = os.path.join(
    log_dir, f"output_log_{timestamp}"
)  # or just "output.log" to overwrite

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),  # also show in terminal
    ],
)

if __name__ == "__main__":
    # Call the scraper
    scrape_rainfall_data()
    logging.info("running public_info_banjir_rainfall.py")
    scrape_waterlevel_data()
    logging.info("running public_info_banjir_waterlevel.py")


# logging.info("🚀 main.py is starting...")
# log by day...

# subprocess.run(["python", "collector/script/public_info_banjir_waterlevel.py"])

# subprocess.run(["python", "collector/script/public_info_banjir_rainfall.py"])
