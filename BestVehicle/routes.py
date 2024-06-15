from flask import render_template, jsonify, redirect, url_for, request
from models import Vehicle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

        try:
            wait = WebDriverWait(driver, 10)
            cars = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="make-model-link kmx-list-item-link"]')))
            prices = wait.until(EC.presence_of_all_elements_located((By.XPATH, '//span[@class="sc--price-miles-info--price"]')))
            
            for car, price in zip(cars, prices):
                car_text = " ".join(car.text.splitlines())
                print(f"Car: {car_text} Price: {price.text}")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            driver.quit()
        
        return redirect(url_for('home'))
