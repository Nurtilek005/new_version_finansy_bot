from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

# Конфигурация доступа
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1MkRsBCAushTSm87tiMZyK0SsqBtMB-HbpTcUdDF0EZM"  # Ваш Spreadsheet ID
CREDENTIALS_FILE = "credentials.json"

# Подключение к Google Sheets
CREDS = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
gc = gspread.authorize(CREDS)
sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Операции")

def add_operation(operation_type, wallet_name, category_name, subcategory_name, currency, amount, comment, check_id):
    """
    Добавляет операцию в лист 'Операции' в правильном порядке.
    """
    try:
        # Получаем текущую дату и время
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Добавляем данные в правильном порядке
        operation_type = "🪙💵Доход" if operation_type == "income" else "💸Расход" if operation_type == "expense" else operation_type

        sheet.append_row([
            date, operation_type, wallet_name, category_name, subcategory_name, currency, amount, comment, check_id
        ])

        print(f"✅ Операция добавлена: {date}, {operation_type}, {wallet_name}, {category_name}, {subcategory_name}, {currency}, {amount}, {comment}, {check_id}")
        return True

    except Exception as e:
        print(f"❌ Ошибка в add_operation: {e}")
        return False
