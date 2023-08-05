import csv
import threading
import os
from tkinter import Tk, Button, Text, Scrollbar, END, filedialog, Label, StringVar, Frame
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def scroll_until_found(driver, index):
    element = None
    scroll_increment = 500
    while element is None:
        try:
            element = WebDriverWait(driver, 0.1).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, f'a[data-index="{index}"]'))
            )
        except:
            current_scroll_position = driver.execute_script("return window.scrollY;")
            driver.execute_script(f"window.scrollTo(0, {current_scroll_position + scroll_increment});")
            time.sleep(0.1)
    return element


class App:
    def __init__(self, root):
        self.is_running = False
        self.root = root
        self.root.title('Rust Skin Scraper')

        self.button_frame = Frame(root)
        self.button_frame.grid(row=0, column=0, sticky="nsew")

        self.start_button = Button(self.button_frame, text="Start", command=self.start, bg='green', fg='white', height=2, width=10)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = Button(self.button_frame, text="Stop", command=self.stop, bg='red', fg='white', height=2, width=10)
        self.stop_button.grid(row=1, column=0, padx=10, pady=10)

        self.save_button = Button(self.button_frame, text="CSV save location", command=self.set_save_location, bg='blue', fg='white', height=2, width=15)
        self.save_button.grid(row=2, column=0, padx=10, pady=10)

        self.save_location = StringVar(root)
        self.save_location.set(os.getcwd())  # Default save location is current directory.
        self.save_location_label = Label(self.button_frame, textvariable=self.save_location)
        self.save_location_label.grid(row=3, column=0, padx=10, pady=10)

        self.scrollbar = Scrollbar(root)
        self.scrollbar.grid(row=0, column=2, sticky="nsew")

        self.text_area = Text(root, yscrollcommand=self.scrollbar.set)
        self.text_area.grid(row=0, column=1, sticky="nsew")

        self.scrollbar.config(command=self.text_area.yview)

        self.status_message = StringVar(root)
        self.status_message.set("Ready")
        self.status_label = Label(root, textvariable=self.status_message, bg='grey')
        self.status_label.grid(row=1, column=0, columnspan=3, sticky="ew")

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.status_message.set("Starting...")
            threading.Thread(target=self.scrape_data).start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.status_message.set("Stopping...")

    def set_save_location(self):
        filename = filedialog.askdirectory()
        if filename:
            self.save_location.set(filename)

    def scrape_data(self):
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options)

        driver.get('https://rustlabs.com/skins')

        total_items = None
        # Scroll once at the start to load the total items count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        filename = os.path.join(self.save_location.get(), 'rust_skins.csv')

        try:
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Skin Name", "Item Name", "Workshop ID"])

                index = 1
                while self.is_running:
                    if total_items is None:
                        try:
                            total_items_element = WebDriverWait(driver, 1).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, '#skins-up-counter'))
                            )
                            total_items = total_items_element.text.split(' / ')[-1]
                        except:
                            pass

                    try:
                        scroll_until_found(driver, index)

                        try:
                            link = scroll_until_found(driver, index)
                            link.click()
                        except Exception as e:
                            print(f"Exception when clicking link at index {index}: {e}")
                            continue

                        try:
                            h1 = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, 'h1'))
                            )
                            skin_name = h1.text
                        except:
                            skin_name = "null"

                        try:
                            item_name_element = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, 'td[data-value]'))
                            )
                            item_name = item_name_element.get_attribute('data-value')
                        except:
                            item_name = "null"

                        try:
                            workshop_id_link = WebDriverWait(driver, 3).until(
                                EC.visibility_of_element_located((By.CSS_SELECTOR, 'td a[rel="nofollow"]'))
                            )
                            workshop_id = workshop_id_link.get_attribute('href').split('?id=')[-1]
                        except:
                            workshop_id = "null"

                        writer.writerow([skin_name, item_name, workshop_id])
                        self.text_area.insert(END, f'{skin_name}, {item_name}, {workshop_id}\n')
                        self.status_message.set(f"{index} out of {total_items}")

                        driver.back()
                        index += 1

                    except Exception as e:
                        print(f"General Exception occurred at index {index}: {e}")
                        break

                self.status_message.set(f"Successfully saved CSV to {filename}")

        except Exception as e:
            self.status_message.set(f"Failed to save CSV: {e}")

        driver.quit()
        self.status_message.set("Stopped")


root = Tk()
app = App(root)
root.mainloop()
