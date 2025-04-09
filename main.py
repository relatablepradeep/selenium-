from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

# ✅ Your ScraperAPI key
API_KEY = 'env'

# ✅ City list
cities = [
    "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune",
    "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", "Nagpur", "Indore", "Patna",
    "Vadodara", "Bhopal", "Chandigarh", "Kochi", "Coimbatore", "Vijayawada",
    "Dehradun", "Haridwar", "Nainital", "Rishikesh", "Haldwani", "Roorkee"
]

# ✅ Setup Chrome options
options = Options()
# options.add_argument("--headless")  # For debugging, comment this out to see browser
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# ✅ Setup Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ Loop through cities
for city in cities:
    print(f"\n📍 Fetching data for city: {city}")
    
    original_url = f"https://www.askapollo.com/physical-appointment/city/{city}"
    scraperapi_url = f"https://api.scraperapi.com/?api_key={API_KEY}&url={original_url}"
    
    try:
        driver.get(scraperapi_url)
        
        # Wait for doctor cards to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "equal-columns"))
        )
        time.sleep(60)

        doctor_cards = driver.find_elements(By.CLASS_NAME, "equal-columns")
        print(f"✅ Found {len(doctor_cards)} doctor(s)")

        for doc in doctor_cards:
            try:
                name = doc.find_element(By.TAG_NAME, "h3").text
                spec_exp = doc.find_element(By.CLASS_NAME, "spec-group").text
                location = doc.find_element(By.TAG_NAME, "address").text
                languages = doc.find_elements(By.CLASS_NAME, "language")[0].text
                qualification = doc.find_elements(By.CLASS_NAME, "language")[1].text
                timing_block = doc.find_element(By.CLASS_NAME, "next-available").text
                photo_url = doc.find_element(By.TAG_NAME, "img").get_attribute("src")

                print(f"""
👨‍⚕️ Name: {name}
🔬 Specialization & Exp: {spec_exp}
🏥 Location: {location}
🌐 Languages: {languages}
🎓 Qualification: {qualification}
🖼️ Photo URL: {photo_url}
⏰ Timings: {timing_block}
--------------------------------------------
""")
            except Exception as inner_err:
                print(f"⚠️ Error extracting a doctor card: {inner_err}")
        
    except Exception as e:
        print(f"❌ Failed to load doctors for city {city}: {e}")

# ✅ Quit the driver at the end
driver.quit()
