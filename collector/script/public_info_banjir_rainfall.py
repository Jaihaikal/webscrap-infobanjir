from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import pandas as pd
import csv
import os



# Set up Edge WebDriver
edge_driver_path = r"D:\PyCode\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service)

current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, '..', 'output', 'rainfall')
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# All states to scrape

states = [
    "Johor",
    "Selangor",
    "Kedah",
    "Perlis",
    "Perak",
    "Melaka",
    "Pahang",
    "Terengganu",
    "Kelantan",
    "Sabah",
    "Sarawak",
    "Negeri Sembilan",
    "Pulau Pinang",
    "Wilayah Persekutuan Kuala Lumpur",
    "Wilayah Persekutuan Labuan",
]

# Final combined headers


def get_soup(driver, url, element_id):
    driver.get(url)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, element_id))
        )
        return BeautifulSoup(driver.page_source, "html.parser")
    except:
        print(f"❌ Failed to load {url}")
        return None

# --------- RAINFALL DATA ----------

rainfall_data = []
today = datetime.today()
rain_days = [(today - timedelta(days=i)).strftime("%d %b %Y") for i in range(6, 0, -1)]
rf_headers = (
    [
        "No",
        "Station ID",
        "Station Name",
        "State",
        "District",
        "Last Update",
        "Type",
    ]
    + rain_days
    + ["Rain Since Midnight", "Rain Last Hour"]
)
for state in states:
    url = f"https://publicinfobanjir.water.gov.my/rainfalldata/{state.replace(' ', '%20')}"
    print(f"🌧️ Scraping Rainfall: {state}")
    soup = get_soup(driver, url, "rainfall-data")
    if not soup:
        continue

    rows = soup.find("tbody", id="rainfall-data").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 13:
            continue  # skip incomplete rows
        try:
            last_hour_tag = cols[12].find("a")
            last_hour_rain = (
                last_hour_tag.text.strip() if last_hour_tag else cols[12].text.strip()
            )

            record = [
                cols[0].text.strip(),
                cols[1].text.strip(),
                cols[2].text.strip(),
                state,
                cols[3].text.strip(),
                cols[4].text.strip(),
                "Rainfall",
                cols[5].text.strip(),
                cols[6].text.strip(),
                cols[11].text.strip(),
                cols[7].text.strip(),
                cols[8].text.strip(),
                cols[9].text.strip(),
                cols[10].text.strip(),
                last_hour_rain,
            ]
            rainfall_data.append(record)
        except Exception as e:
            print(f"⚠️ Rainfall Error ({state}): {e}")


rf_csv_file = os.path.join(output_dir, f"rainfall_data_{timestamp}.csv")
rf_json_file = os.path.join(output_dir, f"rainfall_data_{timestamp}.json")



with open(rf_csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(rf_headers)
    writer.writerows(rainfall_data)

# Save to JSON
df = pd.DataFrame(rainfall_data, columns=rf_headers)
df.to_json(rf_json_file, orient="records", indent=2, force_ascii=False)
# Done

print("✅ Done! rainfall data in: ", output_dir)

driver.quit()
