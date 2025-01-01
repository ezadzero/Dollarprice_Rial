import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTextBrowser
from PyQt5.QtCore import QTimer, QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup

def get_dollar_price():
    url = "https://www.tgju.org/profile/price_dollar_rl"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        price_element = soup.select_one(
            "#main > div.stocks-profile > div.fs-row.bootstrap-fix.widgets.full-w-set.profile-social-share-box > div.row.tgju-widgets-row > div.tgju-widgets-block.col-md-12.col-lg-4.tgju-widgets-block-bottom-unset.overview-first-block > div > div:nth-child(2) > div > div.tables-default.normal > table > tbody > tr:nth-child(1) > td.text-left"
        )
        if price_element:
            return price_element.text.strip()
        else:
            return "قیمت یافت نشد."
    except requests.RequestException as e:
        return f"خطا در دریافت داده‌ها: {e}"

class PriceFetcher(QThread):
    price_fetched = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            price = get_dollar_price()
            self.price_fetched.emit(price)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("قیمت دلار پیگیر")
        # UI components
        self.price_label = QLabel("قیمت دلار: ")
        self.start_button = QPushButton("شروع")
        self.stop_button = QPushButton("پایان")
        self.log_browser = QTextBrowser()
        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.price_label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.log_browser)
        # Set the central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        # Timer setup
        self.timer = QTimer()
        self.timer.timeout.connect(self.fetch_price)
        # Thread setup
        self.fetcher = PriceFetcher()
        self.fetcher.price_fetched.connect(self.update_price)
        self.fetcher.error_occurred.connect(self.display_error)
        # Button connections
        self.start_button.clicked.connect(self.start_fetching)
        self.stop_button.clicked.connect(self.stop_fetching)

    def start_fetching(self):
        self.timer.start(30000)  # 5 minutes in milliseconds
        self.log_browser.append("عملیات شروع شد.")

    def stop_fetching(self):
        self.timer.stop()
        self.log_browser.append("عملیات پایان یافت.")

    def fetch_price(self):
        self.fetcher.start()

    def update_price(self, price):
        self.price_label.setText(f"قیمت دلار: {price}")
        self.log_browser.append(f"قیمت گرفته شده: {price}")

    def display_error(self, error):
        self.log_browser.append(f"خطا: {error}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())