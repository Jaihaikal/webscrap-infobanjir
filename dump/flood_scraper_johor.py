from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import csv

# Step 1: Set up Edge WebDriver
edge_driver_path = r"D:\Program Files\EdgeDriver\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service)

# Step 2: Define state URLs
state_urls = {
    "Johor": "https://publicinfobanjir.water.gov.my/waterleveldata/Johor",
    "Selangor": "https://publicinfobanjir.water.gov.my/waterleveldata/Selangor",
    "Kedah": "https://publicinfobanjir.water.gov.my/waterleveldata/Kedah",
    "Perlis": "https://publicinfobanjir.water.gov.my/waterleveldata/Perlis",
    "Perak": "https://publicinfobanjir.water.gov.my/waterleveldata/Perak",
    "Melaka": "https://publicinfobanjir.water.gov.my/waterleveldata/Melaka",
    "Pahang": "https://publicinfobanjir.water.gov.my/waterleveldata/Pahang",
    "Terengganu": "https://publicinfobanjir.water.gov.my/waterleveldata/Terengganu",
    "Kelantan": "https://publicinfobanjir.water.gov.my/waterleveldata/Kelantan",
    "Sabah": "https://publicinfobanjir.water.gov.my/waterleveldata/Sabah",
    "Sarawak": "https://publicinfobanjir.water.gov.my/waterleveldata/Sarawak",
    "Negeri Sembilan": "https://publicinfobanjir.water.gov.my/waterleveldata/Negeri%20Sembilan",
    "Pulau Pinang": "https://publicinfobanjir.water.gov.my/waterleveldata/Pulau%20Pinang",
    "Wilayah Persekutuan Kuala Lumpur": "https://publicinfobanjir.water.gov.my/waterleveldata/Wilayah%20Persekutuan%20Kuala%20Lumpur",
    "Wilayah Persekutuan Labuan":'https://publicinfobanjir.water.gov.my/waterleveldata/Wilayah%20Persekutuan%20Labuan'
}

# Step 3: Prepare final CSV file
csv_file = "combined_water_levels.csv"

states = [
    "Johor", "Selangor", "Kedah", "Perlis", "Perak", "Melaka", "Pahang", "Terengganu",
    "Kelantan", "Sabah", "Sarawak", "Negeri Sembilan", "Pulau Pinang",
    "Wilayah Persekutuan Kuala Lumpur", "Wilayah Persekutuan Labuan"
]
headers = [
    "No", "Stesen ID", "Nama Stesen", "Negeri", "Daerah", "Lembangan", "Sub Lembangan",
    "Kemaskini Terakhir", "Aras Air", "Normal", "Waspada", "Amaran", "Bahaya", 
]

all_data = []

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    for state_name, url in state_urls.items():
        print(f"🌐 Scraping {state_name}...")

        driver.get(url)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "waterlevel-data"))
            )
        except:
            print(f"❌ Failed to load data for {state_name}")
            continue

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table_body = soup.find("tbody", id="waterlevel-data")
        rows = table_body.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 12:
                continue

            try:
                water_level_tag = cols[7].find("a")
                water_level = water_level_tag.text.strip() if water_level_tag else cols[7].text.strip()

                data = [
                    cols[0].text.strip(),
                    cols[1].text.strip(),
                    cols[2].text.strip(),
                    state_name,  # Add the state column here
                    cols[3].text.strip(),
                    cols[4].text.strip(),
                    cols[5].text.strip(),
                    cols[6].text.strip(),
                    water_level,
                    cols[8].text.strip(),
                    cols[9].text.strip(),
                    cols[10].text.strip(),
                    cols[11].text.strip(),
                ]

                writer.writerow(data)
                all_data.append(data)

            except Exception as e:
                print(f"⚠️ Error parsing row in {state_name}: {e}")

# Step 4: Export to JSON
df = pd.DataFrame(all_data, columns=headers)
df.to_json("combined_water_levels.json", orient="records", indent=2, force_ascii=False)

driver.quit()
print("✅ Done! Combined CSV and JSON saved with data from both Johor and Selangor.")
