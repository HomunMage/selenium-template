from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import hashlib

def hash_title(title: str) -> str:
    return hashlib.sha256(title.encode('utf-8')).hexdigest()

def main():
    url = 'https://www.youtube.com/feed/history'
    profile_path = '/app/profile'

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.profile = profile_path

    driver = webdriver.Remote(
        command_executor='http://selenium-driver:4444/wd/hub',
        options=options
    )

    try:
        print(f"Opening {url} with custom profile")
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-video-renderer"))
        )

        os.makedirs('/app/out', exist_ok=True)
        titles_file = '/app/out/titles.txt'
        hashes_file = '/app/out/title_hashes.txt'

        # Load already saved hashes
        seen_hashes = set()
        if os.path.exists(hashes_file):
            with open(hashes_file, 'r', encoding='utf-8') as f:
                for line in f:
                    seen_hashes.add(line.strip())

        print(f"Loaded {len(seen_hashes)} known hashes")

        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        new_titles_count = 0
        attempts = 0
        max_attempts = 10

        while attempts < max_attempts:
            time.sleep(2)

            video_elements = driver.find_elements(By.CSS_SELECTOR, "ytd-video-renderer h3 a")
            new_titles_found = False

            for el in video_elements:
                title = el.text.strip()
                if title:
                    title_hash = hash_title(title)
                    if title_hash not in seen_hashes:
                        try:
                            with open(titles_file, 'a', encoding='utf-8') as tf, \
                                 open(hashes_file, 'a', encoding='utf-8') as hf:
                                tf.write(title + '\n')
                                hf.write(title_hash + '\n')
                                tf.flush()
                                hf.flush()
                                os.fsync(tf.fileno())
                                os.fsync(hf.fileno())
                            print(f"New title: {title}")
                            seen_hashes.add(title_hash)
                            new_titles_count += 1
                            new_titles_found = True
                        except Exception as e:
                            print(f"Failed to write title or hash: {e}")

            if new_titles_found:
                attempts = 0
            else:
                attempts += 1

            # Scroll to bottom
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.documentElement.scrollHeight")

            if new_height == last_height:
                attempts += 1
            last_height = new_height

        print(f"Finished scrolling. {new_titles_count} new unique titles saved.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
