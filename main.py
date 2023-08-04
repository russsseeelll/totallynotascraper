import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scroll_until_found(driver, index):
    element = None
    while element is None:
        try:
            element = WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f'a[data-index="{index}"]'))
            )
        except:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
    return element



# Setup
options = Options()
options.headless = False
driver = webdriver.Firefox(options=options)

driver.get('https://rustlabs.com/skins')

with open('rust_skins.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Skin Name", "Item Name", "Workshop ID"])

    index = 1
    while True:
        try:
            scroll_until_found(driver, index)

            try:
                link = scroll_until_found(driver, index)
                link.click()
            except Exception as e:
                print(f"Exception when clicking link at index {index}: {e}")
                continue

            try:
                h1 = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1'))
                )
                skin_name = h1.text
            except:
                skin_name = "null"

            try:
                item_name_element = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-value]'))
                )
                item_name = item_name_element.get_attribute('data-value')
            except:
                item_name = "null"

            try:
                workshop_id_link = WebDriverWait(driver, 20).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'td a[rel="nofollow"]'))
                )
                workshop_id = workshop_id_link.text
            except:
                workshop_id = "null"

            writer.writerow([skin_name, item_name, workshop_id])

            driver.back()
            index += 1

        except Exception as e:
            print(f"General Exception occurred at index {index}: {e}")
            break

driver.quit()
