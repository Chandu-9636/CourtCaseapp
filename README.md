# 🧾 Delhi High Court Case Search App

This is a Flask web application that allows users to search for case
details from the Delhi High Court website by entering the case type,
number, and filing year. It uses Selenium for browser automation and
stores each query's HTML response in a local SQLite database.

## ✨ Features

-   Web form to input case details (type, number, year)
-   Automated form submission using Selenium
-   Handles CAPTCHA (text-based only)
-   Extracts parties involved, filing date, and next hearing date
-   Extracts and displays all PDF document links from the result page
-   Stores queries and HTML response in SQLite database

## 📦 Requirements

-   Python 3.x
-   Flask
-   Selenium
-   chromedriver (compatible with your Chrome version)
-   reportlab (for generating PDF)

## 🚀 How to Run

1.  Install the required Python packages.
2.  Run the Flask app: `python app.py`
3.  Open the browser at `http://127.0.0.1:5000/`
4.  Fill the form with case details and submit.
5.  View case details and downloadable PDFs.

## 🛡 License

This project is licensed under the MIT License.
