def scrape_waterlevel_data(output_subfolder="waterlevel", states_to_scrape=None):

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
    output_dir = os.path.join(current_dir, '..', 'output', 'waterlevel')
    os.makedirs(output_dir, exist_ok=True)
    # All states to scrape
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")


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


    # --------- WATER LEVEL DATA ----------
    water_level_data = []

    wl_headers = [
        "No",
        "Station ID",
        "Station Name",
        "State",
        "District",
        "Type",
        "Last Update",
        "Water Level",
        "Normal",
        "Waspada",
        "Amaran",
        "Bahaya",
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
                water_level = (
                    water_level_tag.text.strip()
                    if water_level_tag
                    else cols[7].text.strip()
                )
                record = [
                    cols[0].text.strip(),
                    cols[1].text.strip(),
                    cols[2].text.strip(),
                    state,
                    cols[3].text.strip(),
                    "Water Level",
                    cols[6].text.strip(),
                    water_level,
                    cols[8].text.strip(),
                    cols[9].text.strip(),
                    cols[10].text.strip(),
                    cols[11].text.strip(),
                ]
                water_level_data.append(record)
            except Exception as e:
                print(f"⚠️ Water Level Error ({state}): {e}")

    wl_csv_file = os.path.join(output_dir, f"waterlevel_data_{timestamp}.csv")
    wl_json_file = os.path.join(output_dir, f"waterlevel_data_{timestamp}.json")

    # Save to CSV
    with open(wl_csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(wl_headers)
        writer.writerows(water_level_data)

    # Save to JSON
    df = pd.DataFrame(water_level_data, columns=wl_headers)
    df.to_json(wl_json_file, orient="records", indent=2, force_ascii=False)

    print("✅ Done! water level data")

    driver.quit()
    return water_level_data# Optional return
    # To run:
if __name__ == "__main__":
    scrape_waterlevel_data()


