import time

from PIL import Image
from PIL import ImageEnhance
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_scraped_weatherforecast_image() -> Image:
    # Set the desired viewport size (width, height)
    my_width = 480
    my_height = 850 # will later be cropped
    mobile_emulation = {
        "deviceMetrics": {"width": my_width, "height": my_height, "pixelRatio": 1.0},
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
    }

    # Create an instance of the webdriver with some pre-configured options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("mobileEmulation", mobile_emulation)
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=options)

    # Navigate to webpage
    driver.get("https://openweathermap.org/city/<your_city_id_here>")

    # Wait and find the Cookie Button
    login_button = driver.find_element(By.XPATH, '//*[@id="stick-footer-panel"]/div/div/div/div/div/button')
    # Scroll to it
    driver.execute_script("return arguments[0].scrollIntoView();", login_button)
    # Click the button
    button_clicked = False
    while button_clicked == False:
        try:
            login_button.click()
            button_clicked = True
            print("All cookies successfully accepted!")
        except ElementClickInterceptedException:
            print("Couldn't click the cookie button, retrying...")
            time.sleep(10)

    # hacky wait statement for all the page elements to load
    page_loaded = False
    while page_loaded == False:
        try:
            WebDriverWait(driver, timeout=45).until(
                lambda d: d.find_element(By.XPATH, '//*[@id="weather-widget"]/div[2]/div[1]/div[1]/div[1]/h2').text
                != ""
            )
            page_loaded = True
        except TimeoutException:
            print("Couldn't get the page to load, retrying...")
            time.sleep(60)

    # Scroll to the start of the forecast
    forecast_element = driver.find_element(By.XPATH, '//*[@id="weather-widget"]/div[2]/div[1]/div[1]/div[1]')
    driver.execute_script("return arguments[0].scrollIntoView();", forecast_element)

    # remove the map
    map_element = driver.find_element(By.XPATH, '//*[@id="weather-widget"]/div[2]/div[1]/div[2]')
    driver.execute_script("arguments[0].remove();", map_element)

    # optional: remove the hourly forecast
    # map_element = driver.find_element(By.XPATH, '//*[@id="weather-widget"]/div[2]/div[2]/div[1]')
    # driver.execute_script("arguments[0].remove();", map_element)

    # zoom in a little
    driver.execute_script("document.body.style.zoom='110%'")

    html_element = driver.find_element(By.TAG_NAME, "html")
    driver.execute_script("arguments[0].style.fontSize = '16px';", html_element)

    # Save as a screenshot
    image_filename = "/tmp/openweather_scraped.png"
    driver.save_screenshot(image_filename)

    # Close the WebDriver when done
    driver.quit()

    # crop, resize, enhance & rotate the image for inky 7in5 v2 colour display
    im = Image.open(image_filename, mode="r", formats=None)
    im = im.crop((0, 100, (my_width - 50), (my_height - 50)))
    im = im.resize((480, 800), resample=Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.0)
    im.save(image_filename)
    return im, im


def main():
    _, _ = get_scraped_weatherforecast_image()


if __name__ == "__main__":
    now = time.asctime()
    print(f"It's {now} - running {__name__} in standalone/debug mode")
    main()
