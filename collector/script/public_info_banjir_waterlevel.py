def scrape_waterlevel_data(output_subfolder="waterlevel", states_to_scrape=None):
    from selenium import webdriver
    from selenium.webdriver.edge.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from bs4 import BeautifulSoup
    from datetime import datetime
    import pandas as pd
    import csv
    import os

    # Set up Edge WebDriver
    edge_driver_path = r"D:\PyCode\msedgedriver.exe"
    service = Service(executable_path=edge_driver_path)
    driver = webdriver.Edge(service=service)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "..", "output", output_subfolder)
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if states_to_scrape is None:
        states_to_scrape = [
            "Johor", "Selangor", "Kedah", "Perlis", "Perak", "Melaka", "Pahang",
            "Terengganu", "Kelantan", "Sabah", "Sarawak", "Negeri Sembilan",
            "Pulau Pinang", "Wilayah Persekutuan Kuala Lumpur", "Wilayah Persekutuan Labuan"
        ]

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

    # Headers
    wl_headers = [
        "No", "Station ID", "Station Name", "State", "District", "Lembangan" , "Sub Lembangan" , "Type",
        "Last Update", "Water Level", "Normal", "Waspada", "Amaran", "Bahaya"
    ]

    alert_headers = ["Station ID", "Station Name", "State", "District", "Alert Level"]

    water_level_data = []
    alert_data = []

    # Scraping
    for state in states_to_scrape:
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
                # Grab values
                station_id = cols[1].text.strip() # Station ID
                station_name = cols[2].text.strip() # Station Name
                district = cols[3].text.strip() # District
                lembangan = cols[4].text.strip() # District
                sub_lembangan = cols[5].text.strip() # District
                last_update = cols[6].text.strip() # Last Update

                water_level = float(
                    cols[7].find("a").text.strip() if cols[7].find("a") else cols[7].text.strip()
                )
                normal = float(cols[8].text.strip())
                waspada = float(cols[9].text.strip())
                amaran = float(cols[10].text.strip())
                bahaya = float(cols[11].text.strip())

                # Main record for full CSV
                full_record = [
                    cols[0].text.strip(),  # No
                    station_id,
                    station_name,
                    state,
                    district,
                    lembangan,
                    sub_lembangan,
                    "Water Level",
                    last_update,
                    water_level,
                    normal,
                    waspada,
                    amaran,
                    bahaya,
                ]
                water_level_data.append(full_record)

                # Alert logic
                alert = ""
                if water_level >= bahaya:
                    alert = "Bahaya"
                elif water_level >= amaran:
                    alert = "Amaran"
                elif water_level >= waspada:
                    alert = "Waspada"

                if alert:
                    alert_data.append([
                        station_id,
                        station_name,
                        state,
                        district,
                        alert
                    ])

            except Exception as e:
                print(f"⚠️ Water Level Error ({state}): {e}")

    # Save CSV
    wl_csv_file = os.path.join(output_dir, f"waterlevel_data_{timestamp}.csv")
    with open(wl_csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(wl_headers)
        writer.writerows(water_level_data)

    # Save JSON
    df = pd.DataFrame(water_level_data, columns=wl_headers)
    wl_json_file = os.path.join(output_dir, f"waterlevel_data_{timestamp}.json")
    df.to_json(wl_json_file, orient="records", indent=2, force_ascii=False)

    # Save alerts (optional)
    if alert_data:
        alert_csv_file = os.path.join(output_dir, f"alerts_{timestamp}.csv")
        with open(alert_csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(alert_headers)
            writer.writerows(alert_data)

        print(f"🚨 {len(alert_data)} stations in alert saved to: {alert_csv_file}")

    driver.quit()
    print("✅ Done! All water level data saved.")
    return water_level_data, alert_data
