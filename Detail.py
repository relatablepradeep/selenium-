import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# Load slugs from JSON file
with open('diseases/disease_data.json', 'r', encoding='utf-8') as f:
    diseases_data = json.load(f)

# Output file
output_file = 'scraped_diseases.json'

# Headless browser setup
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)

# Final list to store all scraped data
scraped_data = []

# Loop over diseases
for disease in diseases_data:
    disease_slug = disease['link']
    url = f'{disease_slug}'
    print(f"\n🔗 Scraping: {url}")

    try:
        driver.get(url)
        time.sleep(30)

        # Initialize a dictionary to store the scraped information
        disease_info = {}

        # Header
        try:
            header = driver.find_element(By.CLASS_NAME, 'style__header-section___1o7Yo')
            disease_info['image_url'] = header.find_element(By.TAG_NAME, 'img').get_attribute('src')
            disease_info['disease_name'] = header.find_element(By.TAG_NAME, 'h1').text
            disease_info['brief_text'] = header.find_element(By.CLASS_NAME, 'textSecondary').text
        except NoSuchElementException:
            print("Header section not found.")

        # Overview
        try:
            overview = driver.find_element(By.CLASS_NAME, 'style__overview-section___vgapj')
            disease_info['overview_text'] = overview.find_element(By.TAG_NAME, 'p').text
        except NoSuchElementException:
            print("Overview section not found.")

        # Key Facts
        keyfacts = []
        try:
            keyfacts_section = driver.find_element(By.ID, 'factbox-expandable')
            blocks = keyfacts_section.find_elements(By.CLASS_NAME, 'marginTop-16')

            for block in blocks:
                try:
                    title = block.find_element(By.CLASS_NAME, 'bodyBold').text
                    values = block.find_element(By.CLASS_NAME, 'bodyRegular').text
                    keyfacts.append({
                        'title': title,
                        'values': values.split('\n')
                    })
                except NoSuchElementException:
                    continue
            disease_info['keyfacts'] = keyfacts
        except NoSuchElementException:
            print("Key facts section not found.")

        # Symptoms
        symptoms = []
        try:
            symptoms_section = driver.find_element(By.CLASS_NAME, 'style__dynamic-widget___39jlH')
            elements = symptoms_section.find_elements(By.XPATH, './*')
            current_symptom = {}
            for element in elements:
                if element.tag_name == 'h2':
                    if current_symptom:
                        symptoms.append(current_symptom)
                        current_symptom = {}
                    current_symptom['diseases_name'] = element.text.strip()
                elif element.tag_name == 'p':
                    if 'brief' in current_symptom:
                        current_symptom['brief'] += ' ' + element.text.strip()
                    else:
                        current_symptom['brief'] = element.text.strip()
                elif element.tag_name == 'h3':
                    if current_symptom:
                        symptoms.append(current_symptom)
                        current_symptom = {}
                    current_symptom['disease_type'] = element.text.strip()
                elif element.tag_name == 'p':
                    if 'disease_brief' in current_symptom:
                        current_symptom['disease_brief'] += ' ' + element.text.strip()
                    else:
                        current_symptom['disease_brief'] = element.text.strip()
            if current_symptom:
                symptoms.append(current_symptom)
            disease_info['symptoms'] = symptoms
        except NoSuchElementException:
            print("Symptoms section not found.")

        # Diagnosis
        try:
            diagnosis_container = driver.find_element(By.CLASS_NAME, 'style__dynamic-widget___39jlH')
            disease_info['diagnosis_title'] = diagnosis_container.find_element(By.TAG_NAME, 'h2').text.strip()
            paragraphs = diagnosis_container.find_elements(By.TAG_NAME, 'p')
            disease_info['diagnosis_text'] = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        except NoSuchElementException:
            print("Diagnosis section not found.")

        # Prevention
        try:
            prevention_section = driver.find_element(By.ID, 'prevention')
            disease_info['prevention_title'] = prevention_section.find_element(By.TAG_NAME, 'h2').text.strip()
            disease_info['prevention_text'] = prevention_section.find_element(By.TAG_NAME, 'p').text.strip()
        except NoSuchElementException:
            print("Prevention section not found.")

        # Specialist To Visit
        try:
            specialist_section = driver.find_element(By.ID, 'specialist_to_visit')
            disease_info['specialist_title'] = specialist_section.find_element(By.TAG_NAME, 'h2').text.strip()
            disease_info['specialist_description'] = specialist_section.find_element(By.TAG_NAME, 'p').text.strip()
            specialist_list = specialist_section.find_element(By.TAG_NAME, 'ul')
            specialist_items = specialist_list.find_elements(By.TAG_NAME, 'li')
            disease_info['specialists'] = [item.text.strip() for item in specialist_items]
        except NoSuchElementException:
            print("Specialist to visit section not found.")

        # Home-care
        try:
            home_care_section = driver.find_element(By.ID, 'home-care')
            disease_info['home_care_title'] = home_care_section.find_element(By.TAG_NAME, 'h2').text.strip()
            paragraphs = home_care_section.find_elements(By.TAG_NAME, 'p')
            disease_info['home_care_text'] = paragraphs[0].text.strip() if paragraphs else ""
            disease_info['dos'] = []
            disease_info['donts'] = []
            current_list = None
            for element in home_care_section.find_elements(By.XPATH, './*'):
                if element.tag_name == 'h3' and 'Dos' in element.text:
                    current_list = disease_info['dos']
                elif element.tag_name == 'h3' and 'Don’ts' in element.text:
                    current_list = disease_info['donts']
                elif element.tag_name == 'ul' and current_list is not None:
                    items = element.find_elements(By.TAG_NAME, 'li')
                    for item in items:
                        current_list.append(item.text.strip())
        except NoSuchElementException:
            print("Home-care section not found.")

        # Alternative Therapies
        try:
            alternative_therapies_section = driver.find_element(By.ID, 'alternatives_therapies')
            disease_info['alternative_therapies_title'] = alternative_therapies_section.find_element(By.TAG_NAME, 'h2').text.strip()
            paragraphs = alternative_therapies_section.find_elements(By.TAG_NAME, 'p')
            disease_info['alternative_therapies_text'] = "\n".join([p.text.strip() for p in paragraphs if p.text.strip()])
        except NoSuchElementException:
            print("Alternative therapies section not found.")

        # Add the scraped disease info to the list
        scraped_data.append(disease_info)

    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        continue

# Save the scraped data to a JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(scraped_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ Scraping completed! Data saved to {output_file}")

# Close the browser
driver.quit()
