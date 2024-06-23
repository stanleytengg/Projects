from flask import render_template, redirect, url_for, request
from models import Vehicle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import get_current_matches
import time

def routes(app, db):
    @app.route('/')
    def home():
        return render_template('index.html')

    @app.route('/find_vehicle/')
    def find_vehicle():
        website = 'https://www.carmax.com/'
        driver = webdriver.Chrome()
        driver.get(website)

        input = driver.find_element(By.XPATH, '//input[@id="header-inventory-search"]')
        vehicle_name = request.args.get('add-vehicle')
        input.send_keys(vehicle_name)
        input.send_keys(Keys.RETURN)

        wait = WebDriverWait(driver, 20)
        total_matches = int(driver.find_element(By.XPATH, '//span[@class="header-value hzn-typography--body-1"]').text)

        if total_matches == 0:
            print("No vehicle found")
            return redirect(url_for('home'))
        
        current_matches = get_current_matches(driver)
        start = time.time()
    
        while current_matches < total_matches:
            try:
                extend_button = wait.until(EC.presence_of_element_located((By.XPATH, '//hzn-button[text()="See More Matches"]')))
                driver.execute_script("arguments[0].scrollIntoView(true);", extend_button)
                extend_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//hzn-button[text()="See More Matches"]')))
                driver.execute_script('arguments[0].click();', extend_button)
                wait.until(lambda d: get_current_matches(driver) > current_matches)
                current_matches = get_current_matches(driver)
               
            except Exception as e:
                print(f"Exception occurred: {e}")
                break
        
        try:
            vehicles_info = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="make-model-link kmx-list-item-link"]')))
            prices = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="sc--price-miles-info--price"]')))
            miles = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="sc--price-miles-info--miles"]')))
            
            for vehicle, price, mile in zip(vehicles_info, prices, miles):
                year, name = vehicle.text.split(' ', 1)
                name = name.replace('\n', ' ')
                mile = int(mile.text.replace('K mi', '')) * 1000
                new_vehicle = Vehicle(name=name, year=int(year), price=price.text, miles=mile)
                db.session.add(new_vehicle)
            
            db.session.commit()

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            driver.quit()

        end = time.time()
        duration = round((end - start), 2)
        
        return redirect(url_for('home', duration=duration))
