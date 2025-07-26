from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import time

def main():
    url = 'https://www.youtube.com/feed/history'

    # Path inside container to your mounted profile
    profile_path = '/app/profile'

    options = webdriver.FirefoxOptions()
    options.headless = True
    options.profile = profile_path  # <-- This is the key line

    driver = webdriver.Remote(
        command_executor='http://selenium-driver:4444/wd/hub',
        options=options
    )

    try:
        print(f"Opening {url} with custom profile")
        driver.get(url)
        time.sleep(2)

        body_text = driver.find_element(By.TAG_NAME, "body").text

        os.makedirs('/app/out', exist_ok=True)
        with open('/app/out/out.txt', 'w', encoding='utf-8') as f:
            f.write(body_text)

        print("Page text saved to /app/out/out.txt")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
