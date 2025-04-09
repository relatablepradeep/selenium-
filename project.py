import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ✅ City list
cities = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore", "Patna",
    "Vadodara", "Bhopal", "Chandigarh", "Kochi", "Coimbatore", "Vijayawada",
    "Dehradun", "Haridwar", "Nainital", "Rishikesh", "Haldwani", "Roorkee"
]

# ✅ Create 'data' folder if not exists
os.makedirs("data", exist_ok=True)

# ✅ Set up Chrome driver
options = Options()
# options.add_argument("--headless")  # Uncomment to run headless
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ Start scraping
for city in cities:
    print(f"\n📍 Fetching data for city: {city}")
    url = f"https://www.askapollo.com/physical-appointment/city/{city}"

    try:
        driver.get(url)

        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "equal-columns"))
        )

        time.sleep(5)  # Wait for JS to settle

        doctor_cards = driver.find_elements(By.CLASS_NAME, "equal-columns")
        print(f"✅ Found {len(doctor_cards)} doctor(s) in {city}")

        doctors = []

        for doc in doctor_cards:
            try:
                name = doc.find_element(By.TAG_NAME, "h3").text
                spec_exp = doc.find_element(By.CLASS_NAME, "spec-group").text
                location = doc.find_element(By.TAG_NAME, "address").text
                languages = doc.find_elements(By.CLASS_NAME, "language")[0].text
                qualification = doc.find_elements(By.CLASS_NAME, "language")[1].text
                timing_block = doc.find_element(By.CLASS_NAME, "next-available").text

                # ✅ Extract image src
                try:
                    image = doc.find_element(By.CLASS_NAME, "rounded-circle").get_attribute("src")
                except:
                    image = "N/A"

                doctors.append({
                    "name": name,
                    "specialization_experience": spec_exp,
                    "location": location,
                    "languages": languages,
                    "qualification": qualification,
                    "timing": timing_block,
                    "photo_url": image
                })

            except Exception as doc_error:
                print(f"⚠️ Error parsing one doctor: {doc_error}")

        # ✅ Save to JSON
        with open(f"data/{city}.json", "w", encoding="utf-8") as f:
            json.dump(doctors, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"❌ Failed to load {city}: {e}")

driver.quit()
print("\n🎉 Done. All data saved in the 'data' folder.")
