from selenium import webdriver
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup
import csv
import time

# Step 1: Set up the Edge WebDriver path
edge_driver_path = r"D:\Program Files\EdgeDriver\msedgedriver.exe"
service = Service(executable_path=edge_driver_path)
driver = webdriver.Edge(service=service)

# Step 2: Open the website
driver.get("https://publicinfobanjir.water.gov.my/")

# Step 3: Wait for JavaScript content to load
time.sleep(10)

# Step 4: Get the page HTML
html = driver.page_source

# Step 5: Parse the page with BeautifulSoup
soup = BeautifulSoup(html, "html.parser")
tables = soup.find_all("table")

# Step 6: Save data to CSV
with open("scraped_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    for index, table in enumerate(tables, start=1):
        writer.writerow([f"Table {index}"])  # Label before each table

        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            row_data = []

            for cell in cells:
                text = cell.text.strip()

                # Split "Aras Air" and "Trend" if both exist in the text
                if "Trend:" in text:
                    parts = text.split("Trend:")
                    aras_air = parts[0].strip()
                    trend = parts[1].strip()
                    row_data.extend([aras_air, trend])
                else:
                    row_data.append(text)

            if row_data:
                writer.writerow(row_data)

        writer.writerow([])  # Empty row between tables

# Step 7: Close the browser
driver.quit()

