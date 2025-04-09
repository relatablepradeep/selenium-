import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

# Load slugs from JSON file
with open('diseases/disease_data.json', 'r', encoding='utf-8') as f:
    diseases_data = json.load(f)

# Create output folder if it doesn't exist
output_folder = 'scraped_diseases'
os.makedirs(output_folder, exist_ok=True)

# Setup headless Selenium
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

# List to store all scraped data
scraped_data = []

# Loop through each disease slug
for disease in diseases_data:
    disease_slug = disease['link']
    url = f'{disease_slug}'
    print("\n🔗 Scraping:", url)

    try:
        driver.get(url)
        time.sleep(3)

        # Header Section
        header_section = driver.find_element(By.CLASS_NAME, 'style__header-section___1o7Yo')
        img_tag = header_section.find_element(By.TAG_NAME, 'img')
        image_url = img_tag.get_attribute('src')
        disease_name = header_section.find_element(By.TAG_NAME, 'h1').text
        brief_text = header_section.find_element(By.CLASS_NAME, 'textSecondary').text

        # Overview
        overview_section = driver.find_element(By.ID, 'overview')
        overview_text = overview_section.find_element(By.CLASS_NAME, 'marginTop-8').text

        # Key Facts
        keyfacts_section = driver.find_element(By.ID, 'factbox-expandable')
        keyfacts_blocks = keyfacts_section.find_elements(By.CLASS_NAME, 'marginTop-16')

        keyfacts = []
        for block in keyfacts_blocks:
            try:
                title = block.find_element(By.CLASS_NAME, 'bodyBold').text
                values = block.find_element(By.CLASS_NAME, 'bodyRegular').text
                keyfacts.append({
                    'title': title,
                    'values': values.split('\n')
                })
            except:
                continue

        # Append to list
        scraped_data.append({
            'disease_slug': disease_slug,
            'disease_name': disease_name,
            'image_url': image_url,
            'brief': brief_text,
            'overview': overview_text,
            'key_facts': keyfacts
        })

    except Exception as e:
        print("❌ Error scraping", url, "\n", e)

# Save all scraped data to a JSON file in a different folder
output_path = os.path.join(output_folder, 'all_diseases_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(scraped_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ Scraping complete. Data saved to '{output_path}'")

# Close browser
driver.quit()
