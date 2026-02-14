import argparse
import pathlib
import random
import subprocess
import time

from typing import Union

import pandas as pd

from selenium import webdriver

from selenium.webdriver.remote import webelement

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

TARGET_URL = "https://www.wholefoodsmarket.com"
ITEM_SEARCHES_FILE = "food_no_dupes.csv"
ZIP_CODES_FILE = "zip_codes.txt"
OUTPUT_FILE = "scraped_wf_data.csv"
FIREFOX_INSTALL_LOC = pathlib.Path("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
MAX_ITEM_SEARCHES_PER_ZIP_CODE = 10
PER_BOOK_DELAY_SECONDS = 3


def wait_iter_loop(driver: webdriver.Firefox, by: By, target_element: str, number_of_iterations: int = 10) -> Union[webelement.WebElement, None]:
    wait_iter = 0
    while True:
        if wait_iter >= number_of_iterations:
            break
        try:
            element = driver.find_element(by, target_element)
            return element
        except NoSuchElementException:
            wait_iter += 1
            time.sleep(0.5)

    print(f"Element not found: {target_element}")
    return None


def random_wait_time():
    wait_time = 1 + (random.randrange(1, 2000) / 1000)
    print(f"Waiting {wait_time}")
    return wait_time


def main():
    zip_codes = []
    item_searches = []

    with open(ZIP_CODES_FILE, "r", encoding='utf-8') as f:
        zip_codes = f.readlines()

    items_df = pd.read_csv(ITEM_SEARCHES_FILE)
    item_searches = items_df.description.to_list()

    random.shuffle(item_searches)
    item_searches = item_searches[:min(len(item_searches), MAX_ITEM_SEARCHES_PER_ZIP_CODE)]

    if not pathlib.Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write('zip_code,brand,product_name,price,sale_price,snap_eligible\n')

    script_directory = pathlib.Path().absolute()

    profile_path = pathlib.Path(f"{script_directory}/ff-profile")
    if not profile_path.exists():
        args = [FIREFOX_INSTALL_LOC.as_posix(), "--profile", f'{profile_path.absolute().as_posix()}']
        print(args)
        proc = subprocess.Popen(args)
        proc.wait()
        input("Press anything once you have finished setting up the profile and closed Firefox")

    ff_options = webdriver.FirefoxOptions()
    ff_options.set_preference("dom.webdriver.enabled", False)
    ff_options.set_preference('useAutomationExtension', False)
    ff_options.add_argument("-profile")
    ff_options.add_argument(profile_path.absolute().as_posix())

    driver = webdriver.Firefox(options=ff_options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    driver.get(TARGET_URL)

    print("Completing Cloudflare check...")

    while True:
        try:
            driver.find_element(By.XPATH, "//html/body/div/header/nav/div/div[2]/button/div/div[2]")
            break
        except NoSuchElementException:
            time.sleep(1)

    for zip_code in zip_codes:
        print(f"Selecting: {zip_code}")

        top_level_location_btn = driver.find_element(By.XPATH, "//html/body/div/header/nav/div/div[2]/button/div/div[2]")
        top_level_location_btn.click()

        iframe = wait_iter_loop(driver, By.XPATH, '//*[@id="iframe"]')
        if iframe is None:
            print("Could not find store selector iframe")
            continue

        iframe = driver.find_element(By.XPATH, '//*[@id="iframe"]')
        driver.switch_to.frame(iframe)

        zip_input = wait_iter_loop(driver, By.XPATH, '//*[@id="store-finder-search-bar"]')
        if zip_input is None:
            print("Could not find zip search input")
            continue

        zip_input.clear()
        zip_input.send_keys(zip_code)
        zip_input.send_keys(Keys.RETURN)

        print("Getting store selector")
        store_selector = wait_iter_loop(driver, By.XPATH, "//html/body/main/div/div[3]/wfm-store-list/ul/li[1]/wfm-store-details/div/div[5]/wfm-store-selector/span/span")
        print(f"Got selector: {store_selector}")
        if store_selector is None:
            with open('missed.txt', 'a', encoding='utf-8') as f:
                f.write(zip_code)
            continue
        # Give it a sec to load in all the way since the element ref will be on the tree before it is visible
        time.sleep(2)
        print("Clicking selection button")
        store_selector.click()

        # Give it a sec to register
        time.sleep(2)
        driver.switch_to.default_content()
        print("Getting close btn")
        close_btn = wait_iter_loop(driver, By.XPATH, "//html/body/div[3]/button/span")
        print("Clicking close")
        close_btn.click()

        # The page is gonna reload so wait a few seconds
        time.sleep(2)

        for search_item in item_searches:
            time.sleep(random_wait_time())
            search_input = driver.find_element(By.XPATH, "//html/body/div/header/nav/div/div[3]/div[1]/div/div/form/input")
            search_input.send_keys(search_item)

            search_btn = driver.find_element(By.XPATH, "//html/body/div/header/nav/div/div[3]/div[1]/div/div[1]/form/div/button[2]")
            search_btn.click()

            # Wait a second to avoid freaking out Amazon's servers
            time.sleep(random_wait_time())

            first_item = wait_iter_loop(driver, By.XPATH, "//html/body/div/main/div/div[3]/div[3]/div[1]/a/div[1]/div")
            if first_item is None:
                with open('missed.txt', 'a', encoding='utf-8') as f:
                    f.write(f"{zip_code}: {search_item}\n")
                continue
            first_item.click()

            not_found_brand_metadata_div = 0
            while True:
                if not_found_brand_metadata_div >= 10:
                    break
                try:
                    driver.find_element(
                        By.XPATH, "//html/body/div/main/div[2]/div[2]/div[1]"
                    )
                    break
                except NoSuchElementException:
                    not_found_brand_metadata_div += 1
                    time.sleep(0.5)

            if not_found_brand_metadata_div >= 10:
                with open('missed.txt', 'a', encoding='utf-8') as f:
                    f.write(zip_code)
                continue

            brand = driver.find_element(By.XPATH, "//html/body/div/main/div[2]/div[2]/div[1]").text
            product_name = driver.find_element(By.XPATH, "//html/body/div/main/div[2]/div[2]/div[2]").text
            price = driver.find_element(By.XPATH, "//html/body/div/main/div[2]/div[2]/div[3]/span[1]").text
            sale_price = None
            snap_eligible = False

            try:
                # Snap EBT eligible element
                driver.find_element(By.XPATH, "//html/body/div/main/div[2]/div[2]/div[3]/p[2]")
                snap_eligible = True
            except NoSuchElementException:
                pass

            try:
                # Sale price
                element = driver.find_element(By.XPATH, "//html/body/div/main/div[2]/div[2]/div[3]/span[2]")
                sale_price = price
                price = element.text
            except NoSuchElementException:
                pass

            with open('scraped.csv', 'a', encoding='utf-8') as f:
                f.write(f'{zip_code},"{brand}","{product_name}",{price},{sale_price},{snap_eligible}\n')

    print("Done.")
    driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='scraper')
    main()
