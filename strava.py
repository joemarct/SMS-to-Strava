from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.by import By
from pyvirtualdisplay import Display
from selenium import webdriver
import logging
import time


class Strava(object):

    def __init__(self, headless=True):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.headless = headless
        if self.headless:
            self.display = Display(size=(1440, 800))
            self.display.start()
        profile = FirefoxProfile()
        #profile.set_preference('permissions.default.image', 2)
        self.browser = webdriver.Firefox(firefox_profile=profile)

    def login(self, user_email, user_password):
        self.logger.info('Attempting to login...')
        self.browser.get('http://www.strava.com/routes/new')
        time.sleep(1)
        email = self.browser.find_element_by_name("email")
        email.send_keys(user_email)
        password = self.browser.find_element_by_name("password")
        password.send_keys(user_password)
        loginButton = self.browser.find_element_by_id('login-button')
        loginButton.submit()
        self.logger.info('Login successful!')

    def input_location(self, loc):
        self.logger.info('Registering location...')
        self.locationField = self.browser.find_element_by_css_selector('.input-lg')
        self.locationField.clear()
        self.locationField.send_keys(loc)
        self.locationFieldButton = self.browser.find_element_by_css_selector('.icon')
        self.locationFieldButton.click()
        time.sleep(3)
        canvas = self.browser.find_element_by_xpath('//*[@id="map-canvas"]/div/div[1]/div[2]')
        canvas.click()
        time.sleep(3)

    def save_route(self, loc1, loc2):
        self.logger.info('Saving route...')
        saveButton = self.browser.find_element_by_css_selector('.save-route')
        saveButton.click()
        routeName = self.browser.find_element_by_id('name')
        routeName.send_keys(loc1 + " to " + loc2)
        submitButton = self.browser.find_element_by_css_selector('.submit')
        submitButton.click()
        # Wait for the success message to appear
        try:
            saved_selector = '//h3[text()="Your Route has been saved"]'
            test_elem = EC.visibility_of_element_located((By.XPATH, saved_selector))
            wait = ui.WebDriverWait(self.browser, 20).until(test_elem)
            self.logger.info('Route successfully saved!')
        except TimeoutException:
            pass
    
    def close(self):
        self.browser.quit()
        if self.headless:
            self.display.stop()
            

def create_route(email,password, loc1, loc2):
    s = Strava()
    s.login(email, password)
    s.input_location(loc1)
    s.input_location(loc2)
    s.save_route(loc1, loc2)
    s.close()
    

if __name__ == '__main__':
    import sys
    email, password, loc1, loc2 = sys.argv[1:]
    strava_interface(email, password, loc1, loc2)

