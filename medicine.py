import os
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Setup Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Remove if you want to see browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Amazon search settings
search_query = "medical+products"
base_url = f"https://www.amazon.in/s?k={search_query}&page="
total_pages = 3  # how many pages to scrape

# Create folder to store output
folder_name = "medical"
os.makedirs(folder_name, exist_ok=True)

# Results array
all_results = []

# Loop through Amazon pages
for page in range(1, total_pages + 1):
    print(f"Scraping page {page}...")
    driver.get(base_url + str(page))
    time.sleep(5)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    products = soup.select('div[data-component-type="s-search-result"]')

    for product in products:
        try:
            asin = product.get("data-asin")

            title_tag = product.select_one("h2.a-size-base-plus")
            title = title_tag.get_text(strip=True) if title_tag else None

            img_tag = product.select_one("img.s-image")
            image_url = img_tag["src"] if img_tag else None

            rating_tag = product.select_one("span.a-icon-alt")
            rating = rating_tag.get_text(strip=True) if rating_tag else None

            review_tag = product.select_one("div[data-cy='reviews-block'] span.a-size-small.puis-normal-weight-text")
            reviews = review_tag.get_text(strip=True) if review_tag else None

            price_link_tag = product.select_one("a.a-link-normal.s-no-hover")
            price_link = "https://www.amazon.in" + price_link_tag["href"] if price_link_tag else None

            price_tag = product.select_one("span.a-price > span.a-offscreen")
            price = price_tag.get_text(strip=True) if price_tag else None

            all_results.append({
                "asin": asin,
                "title": title,
                "image_url": image_url,
                "rating": rating,
                "reviews": reviews,
                "price_link": price_link,
                "actual_price": price
            })

        except Exception as e:
            print("Error while processing a product:", e)

# Close browser
driver.quit()

# Save JSON file
output_path = os.path.join(folder_name, "amazon_medical_products.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print(f"\n✅ Scraped {len(all_results)} products and saved to '{output_path}'")
