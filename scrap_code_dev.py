from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv
from datetime import datetime, timedelta


# Set up Edge WebDriver
edge_driver_path = r"D:\PyCode\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service)

# All states to scrape

states = [
    "Johor", "Selangor", "Kedah", "Perlis", "Perak", "Melaka", "Pahang", "Terengganu",
    "Kelantan", "Sabah", "Sarawak", "Negeri Sembilan", "Pulau Pinang",
    "Wilayah Persekutuan Kuala Lumpur", "Wilayah Persekutuan Labuan"
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

# --------- WATER LEVEL DATA ----------
water_level_data = []

wl_headers =  [
    "No", "Station ID", "Station Name", "State", "District", "Type", "Last Update",
    "Water Level", "Normal", "Waspada", "Amaran", "Bahaya",
   
]

for state in states:
    url = f"https://publicinfobanjir.water.gov.my/waterleveldata/{state.replace(' ', '%20')}"
    print(f"🌊 Scraping Water Level: {state}")
    soup = get_soup(driver, url, "waterlevel-data")
    if not soup:
        continue

    rows = soup.find("tbody", id="waterlevel-data").find_all("tr")
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 12:
            continue
        try:
            water_level_tag = cols[7].find("a")
            water_level = water_level_tag.text.strip() if water_level_tag else cols[7].text.strip()
            record = [
                cols[0].text.strip(),
                cols[1].text.strip(), 
                cols[2].text.strip(), 
                state,
                cols[3].text.strip(), 
                "Water", 
                cols[6].text.strip(),
                # Type = Water
                water_level, 
                cols[8].text.strip(), 
                cols[9].text.strip(), 
                cols[10].text.strip(), 
                cols[11].text.strip(),
                # Rain data fields are empty
            ]
            water_level_data.append(record)
        except Exception as e:
            print(f"⚠️ Water Level Error ({state}): {e}")
            
wl_csv_file = "water_level_data.csv"
wl_json_file = "water_level_data.json"

# Save to CSV
with open(wl_csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(wl_headers)
    writer.writerows(water_level_data)

# Save to JSON
df = pd.DataFrame(water_level_data, columns=wl_headers)
df.to_json(wl_json_file, orient="records", indent=2, force_ascii=False)

print("✅ Done! water level data")

# --------- RAINFALL DATA ----------

rainfall_data = []
today = datetime.today()
rain_days = [(today - timedelta(days=i)).strftime("%d %b %Y") for i in range(5, 0, -1)]
rf_headers = [
    "No", "Station ID", "Station Name", "State", "District", "Last Update", "Type",
    "Rain 10 Apr", ] + rain_days + [ 
    "Rain Since Midnight", "Rain Last Hour"
]
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
            last_hour_rain = last_hour_tag.text.strip() if last_hour_tag else cols[12].text.strip()

            record = [
                cols[0].text.strip(),  # No
                cols[1].text.strip(),  # Station ID
                cols[2].text.strip(),  # Station Name
                state,
                cols[3].text.strip(),  # District
                cols[4].text.strip(),  # Last Update
                "Rainfall",
                cols[5].text.strip(),  # Rain 10 Apr
                cols[6].text.strip(),  # Rain 11 Apr
                cols[7].text.strip(),  # Rain 12 Apr
                cols[8].text.strip(),  # Rain 13 Apr
                cols[9].text.strip(),  # Rain 14 Apr
                cols[10].text.strip(), # Rain 15 Apr
                cols[11].text.strip(), # Rain Since Midnight
                last_hour_rain         # Rain Last Hour
            ]
            rainfall_data.append(record)
        except Exception as e:
            print(f"⚠️ Rainfall Error ({state}): {e}")

# --------- SAVE TO CSV & JSON ---------


rf_csv_file = "rainfall_data.csv"
rf_json_file = "rainfall_data.json"

with open(rf_csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(rf_headers)
    writer.writerows(rainfall_data)

# Save to JSON
df = pd.DataFrame(rainfall_data, columns=rf_headers)
df.to_json(rf_json_file, orient="records", indent=2, force_ascii=False)
# Done
print("✅ Done! rainfall data")
driver.quit()
