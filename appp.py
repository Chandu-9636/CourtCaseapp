from flask import Flask, render_template, request, redirect, url_for, flash
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sqlite3
import datetime
import os
import time
import re
app = Flask(__name__)
app.secret_key = 'secret123'
DB_PATH = 'queries.db'

# Setup DB
if not os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE queries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_type TEXT,
        case_number TEXT,
        filing_year TEXT,
        query_time TIMESTAMP,
        raw_html TEXT
    )""")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/search', methods=['POST'])
def search():
    case_type = request.form['case_type']
    case_number = request.form['case_number']
    filing_year = request.form['filing_year']

    try:
        # Set up headless browser
        options = Options()
        # Comment next line if you want to see the browser
        # options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver.get('https://delhihighcourt.nic.in/app/get-case-type-status')

        time.sleep(3)

        # Fill form
        driver.find_element(By.ID, 'case_type').send_keys(case_type)
        driver.find_element(By.ID, 'case_number').send_keys(case_number)
        driver.find_element(By.ID, 'case_year').send_keys(filing_year)
        captcha=driver.find_element(By.ID, 'captcha-code').text.strip()
        driver.find_element(By.ID, 'captchaInput').send_keys(captcha)
        time.sleep(1)
        try:
        	#driver.find_element(By.XPATH, '//*[@id="search"]').click()
        	WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.ID, 'search'))).click()
        	time.sleep(2)
        except Exception as e:
        	flash(e)

        # Wait for results to load
        time.sleep(3)
        page_source = driver.page_source
        time.sleep(3)

        # Extract result details
        try:
        	parties = driver.find_element(By.XPATH, '//*[@id="caseTable"]/tbody/tr/td[3]').text.strip()
        except Exception:
        	parties='Not Available'
        try:
        	fil_date = driver.find_element(By.XPATH, '//*[@id="caseTable"]/tbody/tr/td[4]').text.strip()
        	match=re.search(r'/(\d{4})',fil_date)
        	filing_date=match.group(1) if match else 'Not Available'
        	
        except Exception:
        	filing_date='Not Available'
        try:
        	next_hearing = driver.find_element(By.XPATH, '//*[@id="caseTable"]/tbody/tr/td[2]').text.strip()
            text_td=next_hearing.text
        	match=re.search(r'Next Hearing:(\d+)',text_td)
        	if match:
        		next_hearing=match.group(1)
        except Exception:
        	next_hearing='Not Available'
        # Extract PDF links
        pdf_links = []
        links = driver.find_elements(By.TAG_NAME, 'a')
        for link in links:
            href = link.get_attribute('href')
            if href and href.endswith('.pdf'):
            	pdf_links.append(href)

        # Save to DB
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO queries (case_type, case_number, filing_year, query_time, raw_html) VALUES (?, ?, ?, ?, ?)",
                  (case_type, case_number, filing_year, datetime.datetime.now(), page_source))
        conn.commit()
        conn.close()

        driver.quit()

        return render_template('result.html', parties=parties, filing_date=filing_date,
                               next_hearing=next_hearing, pdf_links=pdf_links)

    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

