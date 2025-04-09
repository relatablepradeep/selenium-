import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# Setup Chrome options
options = Options()
options.add_argument('--headless')  # run in background
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

# Set up driver (adjust path if needed)
driver = webdriver.Chrome(options=options)

# Create output folder
output_dir = "diseases"
os.makedirs(output_dir, exist_ok=True)

# Initialize list for all disease data
diseases_data = []

# Iterate from A to Z
for letter in range(ord('A'), ord('Z') + 1):
    url = f"https://www.1mg.com/all-diseases?label={chr(letter)}"
    print(f"Scraping page: {url}")
    driver.get(url)
    time.sleep(2)  # wait for content to load

    try:
        cards = driver.find_elements(By.CLASS_NAME, "style__product-card___1gbex")
        for card in cards:
            try:
                name_element = card.find_element(By.CLASS_NAME, "style__product-name___HASYw")
                disease_name = name_element.text.strip()
                link = "https://www.1mg.com" + name_element.get_attribute("href")

                img_element = card.find_element(By.TAG_NAME, "img")
                img_url = img_element.get_attribute("src")
                img_alt = img_element.get_attribute("alt")

                diseases_data.append({
                    "disease_name": disease_name,
                    "link": link,
                    "image_url": img_url,
                    "alt_text": img_alt
                })

            except Exception as e:
                print(f"❌ Error parsing a card: {e}")
    except Exception as e:
        print(f"❌ Error on page {url}: {e}")

# Save as JSON
output_file = os.path.join(output_dir, "disease_data.json")
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(diseases_data, f, ensure_ascii=False, indent=4)

driver.quit()
print(f"✅ Done! Data saved to {output_file}")
