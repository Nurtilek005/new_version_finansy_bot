import json
import os

JSON_FILE = "data.json"


def load_data():
    """Загружает данные и исправляет структуру, если в кошельках есть 'income' и 'expense'."""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if "wallets" not in data or not isinstance(data["wallets"], dict):
            data["wallets"] = {}

        # Удаляем ошибочные 'income' и 'expense', если они вдруг попали в список кошельков
        if "income" in data["wallets"]:
            del data["wallets"]["income"]
        if "expense" in data["wallets"]:
            del data["wallets"]["expense"]

        save_data(data)  # ✅ Сохраняем исправленную структуру

        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {"wallets": {}}  # Если файл не найден или поврежден, создаем новый


def save_data(data):
    """Сохраняет данные в JSON без удаления ключей income и expense."""

    # Проверяем, что структура "wallets" не повреждена
    if "wallets" not in data:
        data["wallets"] = {}

    with open(JSON_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def check_wallet_balance(wallet_name):
    """Возвращает текущий баланс кошелька."""
    data = load_data()

    balance_income = data["wallets"].get("income", {}).get(wallet_name, {}).get("balance", 0)
    balance_expense = data["wallets"].get("expense", {}).get(wallet_name, {}).get("balance", 0)

    return balance_income - balance_expense  # Итоговый баланс (доход - расход)


def check_balance(wallet_name, amount):
    """Проверяет, достаточно ли денег в кошельке для расхода."""
    current_balance = check_wallet_balance(wallet_name)

    if current_balance < amount:
        return False, current_balance  # Недостаточно средств

    return True, current_balance  # Денег хватает


def add_wallet(wallet_name):
    """
    Добавляет новый кошелек с единственным балансом.
    """
    data = load_data()

    if wallet_name in data["wallets"]:
        print(f"❌ Ошибка: кошелек '{wallet_name}' уже существует.")
        return False

    # Создаем кошелек с общим балансом
    data["wallets"][wallet_name] = {
        "balance": 0,  # ✅ Теперь баланс хранится здесь
        "expense": {
            "categories": {}  # Категории расходов
        },
        "income": {
            "categories": {}  # Категории доходов
        }
    }

    save_data(data)
    print(f"✅ Кошелек '{wallet_name}' успешно создан!")
    return True


def subtract_expense(wallet_name, amount):
    """
    Вычитает сумму расхода из баланса кошелька.
    """
    data = load_data()

    if wallet_name not in data["wallets"]:
        print(f"❌ Ошибка: кошелек '{wallet_name}' не найден.")
        return False

    if data["wallets"][wallet_name]["balance"] < amount:
        print(f"❌ Ошибка: недостаточно средств в кошельке '{wallet_name}'.")
        return False

    # ✅ Вычитаем деньги из общего баланса
    data["wallets"][wallet_name]["balance"] -= amount
    save_data(data)
    return True


def add_income(wallet_name, amount):
    """
    Добавляет сумму дохода в баланс кошелька.
    """
    data = load_data()

    if wallet_name not in data["wallets"]:
        print(f"❌ Ошибка: кошелек '{wallet_name}' не найден.")
        return False

    # ✅ Добавляем деньги в общий баланс
    data["wallets"][wallet_name]["balance"] += amount
    save_data(data)
    return True


def update_wallet_balance(wallet_name, amount, operation_type):
    """
    Обновляет баланс кошелька после дохода или расхода.
    Если операция "income", сумма добавляется.
    Если операция "expense", сумма вычитается.
    """
    data = load_data()

    if wallet_name not in data["wallets"]:
        print(f"❌ Ошибка: кошелек '{wallet_name}' не найден.")
        return False

    # Проверяем, есть ли поле "balance" в кошельке
    if "balance" not in data["wallets"][wallet_name]:
        data["wallets"][wallet_name]["balance"] = 0

    if operation_type == "income":
        data["wallets"][wallet_name]["balance"] += amount  # Добавляем деньги
    elif operation_type == "expense":
        if data["wallets"][wallet_name]["balance"] < amount:
            print(f"❌ Ошибка: недостаточно средств в кошельке '{wallet_name}'.")
            return False
        data["wallets"][wallet_name]["balance"] -= amount  # Вычитаем деньги

    save_data(data)  # Сохраняем изменения
    return True


def delete_wallet(wallet_name):
    """
    Удаляет кошелек и его валюты, но не позволяет удалять 'income' и 'expense'.
    """
    data = load_data()

    if wallet_name.lower() in ["income", "expense"]:
        print(f"❌ Ошибка: '{wallet_name}' не является кошельком и не может быть удалено.")
        return False

    if wallet_name not in data["wallets"]:
        print(f"❌ Ошибка: кошелек '{wallet_name}' не найден.")
        return False

    del data["wallets"][wallet_name]
    save_data(data)
    print(f"✅ Кошелек '{wallet_name}' успешно удален!")
    return True


def get_wallets():
    """Возвращает список всех кошельков, исключая системные записи 'income' и 'expense'."""
    data = load_data()

    # Убираем "income" и "expense", если они есть
    wallets = [wallet for wallet in data["wallets"] if wallet not in ["income", "expense"]]

    return wallets  # Возвращаем только реальные кошельки


def add_category(wallet_name, operation_type, category_name):
    """Добавляет категорию в кошелек."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False

    if category_name in data["wallets"][operation_type][wallet_name]["categories"]:
        return False  # Категория уже существует

    data["wallets"][operation_type][wallet_name]["categories"][category_name] = {"subcategories": {}}
    save_data(data)
    return True


def delete_category(wallet_name, operation_type, category_name):
    """Удаляет категорию из кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return False

    del data["wallets"][operation_type][wallet_name]["categories"][category_name]
    save_data(data)
    return True


def get_categories(wallet_name, operation_type):
    """Возвращает список категорий для кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return []

    return list(data["wallets"][operation_type][wallet_name]["categories"].keys())


def add_subcategory(wallet_name, operation_type, category_name, subcategory_name):
    """Добавляет подкатегорию в категорию кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return False
    if subcategory_name in data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"]:
        return False  # Подкатегория уже существует

    data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][subcategory_name] = {
        "currencies": {}}
    save_data(data)
    return True


def delete_subcategory(wallet_name, operation_type, category_name, subcategory_name):
    """Удаляет подкатегорию из категории кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return False
    if subcategory_name not in data["wallets"][operation_type][wallet_name]["categories"][category_name][
        "subcategories"]:
        return False

    del data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][subcategory_name]
    save_data(data)
    return True


def get_subcategories(wallet_name, operation_type, category_name):
    """Возвращает список подкатегорий для категории кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return []
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return []

    return list(data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"].keys())


def add_currency(wallet_name, operation_type, category_name, subcategory_name, currency_name):
    """Добавляет валюту в подкатегорию кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return False
    if subcategory_name not in data["wallets"][operation_type][wallet_name]["categories"][category_name][
        "subcategories"]:
        return False
    if currency_name in data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][
        subcategory_name]["currencies"]:
        return False  # Валюта уже существует

    data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][subcategory_name][
        "currencies"][currency_name] = {}
    save_data(data)
    return True


def delete_currency(wallet_name, operation_type, category_name, subcategory_name, currency_name):
    """Удаляет валюту из подкатегории кошелька."""
    data = load_data()

    if wallet_name not in data["wallets"][operation_type]:
        return False
    if category_name not in data["wallets"][operation_type][wallet_name]["categories"]:
        return False
    if subcategory_name not in data["wallets"][operation_type][wallet_name]["categories"][category_name][
        "subcategories"]:
        return False
    if currency_name not in data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][
        subcategory_name]["currencies"]:
        return False

    del data["wallets"][operation_type][wallet_name]["categories"][category_name]["subcategories"][subcategory_name][
        "currencies"][currency_name]
    save_data(data)
    return True


def get_currencies(wallet_name):
    """
    Возвращает список валют для указанного кошелька.
    """
    data = load_data()
    wallet = data.get("wallets", {}).get(wallet_name, {})

    # Если в кошельке нет валют, создаем пустой список
    if "currencies" not in wallet:
        wallet["currencies"] = []
        save_data(data)

    return wallet["currencies"]


def migrate_json_structure():
    """
    Проверяет и обновляет структуру JSON-файла, добавляя отсутствующие ключи и исправляя подкатегории.
    """
    data = load_data()

    # Гарантируем, что структура имеет разделение на доходы и расходы
    if "wallets" not in data:
        data["wallets"] = {"income": {}, "expense": {}}

    for operation_type in ["income", "expense"]:
        if operation_type not in data["wallets"]:
            data["wallets"][operation_type] = {}

        for wallet_name, wallet_data in data["wallets"][operation_type].items():
            # Убеждаемся, что у кошелька есть "balance" и "categories"
            if "balance" not in wallet_data:
                wallet_data["balance"] = 0
            if "categories" not in wallet_data:
                wallet_data["categories"] = {}

            for category_name, category_data in wallet_data["categories"].items():
                # Гарантируем, что у категории есть "subcategories"
                if "subcategories" not in category_data:
                    category_data["subcategories"] = {}

                for subcategory_name, subcategory_data in category_data["subcategories"].items():
                    # Гарантируем, что у подкатегории есть "currencies"
                    if "currencies" not in subcategory_data:
                        subcategory_data["currencies"] = {}

    save_data(data)
    print("✅ JSON-структура успешно обновлена!")
