from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Set up Edge WebDriver
edge_driver_path = r"D:\Program Files\EdgeDriver\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service)

# All states to scrape
states = [
    "Johor", "Selangor", "Kedah", "Perlis", "Perak", "Melaka", "Pahang", "Terengganu",
    "Kelantan", "Sabah", "Sarawak", "Negeri Sembilan", "Pulau Pinang",
    "Wilayah Persekutuan Kuala Lumpur", "Wilayah Persekutuan Labuan"
]

# Final combined headers
headers = [
    "No", "Station ID", "Station Name", "State", "District", "Type", "Last Update",
    "Water Level", "Normal", "Waspada", "Amaran", "Bahaya",
    "Rain 10 Apr", "Rain 11 Apr", "Rain 12 Apr", "Rain 13 Apr", "Rain 14 Apr", "Rain 15 Apr",
    "Rain Since Midnight", "Rain Last Hour"
]

all_data = []

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
                cols[0].text.strip(), cols[1].text.strip(), cols[2].text.strip(), state,
                cols[3].text.strip(), "Water", cols[6].text.strip(),  # Type = Water
                water_level, cols[8].text.strip(), cols[9].text.strip(), cols[10].text.strip(), cols[11].text.strip(),
                "", "", "", "", "", "", "", ""  # Rain data fields are empty
            ]
            all_data.append(record)
        except Exception as e:
            print(f"⚠️ Water Level Error ({state}): {e}")

# --------- RAINFALL DATA ----------
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
            continue
        try:
            last_hour_tag = cols[12].find("a")
            last_hour_rain = last_hour_tag.text.strip() if last_hour_tag else cols[12].text.strip()
            record = [
                cols[0].text.strip(), cols[1].text.strip(), cols[2].text.strip(), state,
                cols[3].text.strip(), "Rainfall", cols[4].text.strip(),  # Type = Rainfall
                "", "", "", "", "",  # Water Level fields empty
                cols[5].text.strip(), cols[6].text.strip(), cols[7].text.strip(), cols[8].text.strip(),
                cols[9].text.strip(), cols[10].text.strip(),
                cols[11].text.strip(),  # Rain since midnight
                last_hour_rain        # Rain last hour
            ]
            all_data.append(record)
        except Exception as e:
            print(f"⚠️ Rainfall Error ({state}): {e}")

# --------- SAVE TO CSV & JSON ---------
csv_file = "combined_data.csv"
json_file = "combined_data.json"

# Save to CSV
with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(all_data)

# Save to JSON
df = pd.DataFrame(all_data, columns=headers)
df.to_json(json_file, orient="records", indent=2, force_ascii=False)

# Done
driver.quit()
print("✅ Done! Combined data saved to 'combined_data.csv' and 'combined_data.json'")
