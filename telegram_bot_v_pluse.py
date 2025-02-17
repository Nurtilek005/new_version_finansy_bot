# import asyncio
# from telegram import ReplyKeyboardMarkup, KeyboardButton
#
# import logging
# import uuid
# from datetime import datetime
# from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
# from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
# from google_sheets import add_operation, SPREADSHEET_ID, gc
# from json_manager import add_wallet, get_wallets, add_category, get_categories, add_subcategory, get_subcategories, \
#     delete_wallet, delete_category, delete_subcategory, get_currencies, add_currency, delete_currency, \
#     migrate_json_structure, load_data, check_balance, check_wallet_balance, update_wallet_balance, save_data
#
# GROUP_CHAT_ID =  -1002304215716  # Замените на ваш реальный ID группы
#
#
#
# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Главное меню: показывает список кошельков + кнопки."""
#     data = load_data()
#     wallets = data.get("wallets", {})
#
#     buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
#     buttons.append([InlineKeyboardButton("💰 Показать баланс кошелька", callback_data="show_wallets_balance")])
#     buttons.append([InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")])
#     buttons.append([InlineKeyboardButton("🗑 Удалить кошелек", callback_data="delete_wallet")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#
#     # ✅ **Добавляем кнопки в панель ввода сообщений (ReplyKeyboardMarkup)**
#
#     if update.message:
#         await update.message.reply_text("💰 Выберите кошелек или действие:", reply_markup=reply_markup)
#     elif update.callback_query and update.callback_query.message:
#         await update.callback_query.message.edit_text("💰 Выберите кошелек или действие:", reply_markup=reply_markup)
#     else:
#         logging.error("Ошибка в start(): update.callback_query.message = None")
#
# def generate_check_id():
#     """
#     Генерирует уникальный ID для чека.
#     """
#     return str(uuid.uuid4())[:8]  # Возвращаем первые 8 символов UUID
#
#
# async def show_wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     data = load_data()
#     wallets = data.get("wallets", {})
#
#     buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
#     buttons.append([InlineKeyboardButton("💰 Показать баланс кошелька", callback_data="show_wallets_balance")])
#     buttons.append([InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")])
#     buttons.append([InlineKeyboardButton("🗑 Удалить кошелек", callback_data="delete_wallet")])
#
#     # Добавляем обновление и сообщение об ошибке
#     buttons.append([
#         InlineKeyboardButton("🔄 Обновить", callback_data="refresh"),
#         InlineKeyboardButton("⚠️ Сообщить об ошибке ❗", callback_data="report_issue")
#     ])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#
#     if update.callback_query and update.callback_query.message:
#         await update.callback_query.message.edit_text("💰 Выберите кошелек:", reply_markup=reply_markup)
#     elif update.message:
#         await update.message.reply_text("💰 Выберите кошелек:", reply_markup=reply_markup)
#     else:
#         logging.error("Ошибка в show_wallet_menu(): update.callback_query и update.message = None")
#
#
# async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню категорий для выбранного кошелька.
#     """
#     try:
#         operation_type = context.user_data.get("operation_type")
#         wallet_name = context.user_data.get("selected_wallet")
#
#         if not operation_type or not wallet_name:
#             if update.callback_query:
#                 await update.callback_query.edit_message_text("Ошибка: тип операции или кошелек не выбраны.")
#             else:
#                 await update.message.reply_text("Ошибка: тип операции или кошелек не выбраны.")
#             return
#
#         categories = get_categories(operation_type, wallet_name)
#
#         buttons = [
#             [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
#             [InlineKeyboardButton(" 🗑 Удалить категорию", callback_data="delete_category")],
#         ]
#
#         for category in categories:
#             buttons.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])
#
#         buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")])
#         reply_markup = InlineKeyboardMarkup(buttons)
#
#         if update.callback_query:
#             await update.callback_query.edit_message_text(
#                 text=f"Категории для кошелька '{wallet_name}':",
#                 reply_markup=reply_markup
#             )
#         else:
#             await update.message.reply_text(
#                 text=f"Категории для кошелька '{wallet_name}':",
#                 reply_markup=reply_markup
#             )
#     except Exception as e:
#         logging.error(f"Ошибка в show_categories: {e}")
#         if update.callback_query:
#             await update.callback_query.edit_message_text("Произошла ошибка при загрузке категорий.")
#         else:
#             await update.message.reply_text("Произошла ошибка при загрузке категорий.")
#
# async def show_currency_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню выбора валюты внутри кошелька (единый список для всех категорий).
#     """
#     wallet_name = context.user_data.get("selected_wallet")
#
#     if not wallet_name:
#         await update.callback_query.edit_message_text("❌ Ошибка: кошелек не выбран.")
#         return
#
#     currencies = get_currencies(wallet_name)
#
#     if not currencies:
#         await update.callback_query.edit_message_text(
#             "❌ В этом кошельке пока нет валют. Добавьте валюту!",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")],
#                 [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
#             ])
#         )
#         return
#
#     buttons = [[InlineKeyboardButton(currency, callback_data=f"currency_{currency}")] for currency in currencies]
#     buttons.append([InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")])
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])
#
#     await update.callback_query.edit_message_text("Выберите валюту:", reply_markup=InlineKeyboardMarkup(buttons))
#
# async def show_subcategories(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню подкатегорий для выбранной категории.
#     """
#     try:
#         operation_type = context.user_data.get("operation_type")
#         wallet_name = context.user_data.get("selected_wallet")
#         category_name = context.user_data.get("selected_category")
#
#         if not operation_type or not wallet_name or not category_name:
#             await update.message.reply_text("Ошибка: категория больше не существует. Выберите новую.")
#             return
#
#         # Проверяем, существует ли категория
#         categories = get_categories(operation_type, wallet_name)
#         if category_name not in categories:
#             await update.message.reply_text("Ошибка: выбранная категория была удалена. Выберите новую.")
#             await back_to_category_menu(update, context)
#             return
#
#         # Получаем подкатегории
#         subcategories = get_subcategories(operation_type, wallet_name, category_name)
#
#         # Создаём кнопки подкатегорий
#         buttons = [
#             [InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")]
#             for subcat in subcategories
#         ]
#         buttons.append([InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")])
#         buttons.append([InlineKeyboardButton("🗑 Удалить подкатегорию", callback_data="delete_subcategory")])  # Кнопка удаления
#         buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])
#
#         reply_markup = InlineKeyboardMarkup(buttons)
#
#         # Отправляем меню
#         if update.callback_query:
#             await update.callback_query.edit_message_text(
#                 text=f"Категория: {category_name}\nВыберите подкатегорию:",
#                 reply_markup=reply_markup
#             )
#         else:
#             await update.message.reply_text(
#                 text=f"Категория: {category_name}\nВыберите подкатегорию:",
#                 reply_markup=reply_markup
#             )
#     except Exception as e:
#         logging.error(f"Ошибка в show_subcategories: {e}")
#         await update.message.reply_text("Произошла ошибка при загрузке подкатегорий. Попробуйте снова.")
#
# async def back_to_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Возвращает пользователя в меню категорий.
#     """
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#
#     # Проверяем, выбраны ли тип операции и кошелек
#     if not operation_type or not wallet_name:
#         await query.edit_message_text("Ошибка: тип операции или кошелек не выбраны.")
#         return
#
#     # Получаем обновленный список категорий
#     categories = get_categories(operation_type, wallet_name)
#
#     # Проверяем, есть ли категории
#     if not categories:
#         await query.edit_message_text("Категорий нет. Добавьте новую категорию.",
#                                       reply_markup=InlineKeyboardMarkup([
#                                           [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
#                                           [InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")]
#                                       ]))
#         return
#
#     # Создаем кнопки для категорий
#     buttons = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
#     buttons.append([InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")])
#     buttons.append([InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")])
#     buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text("Выберите категорию:", reply_markup=reply_markup)
#
# async def back_to_subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Возвращает пользователя в меню подкатегорий.
#     """
#     query = update.callback_query
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#
#     # Проверяем, выбраны ли кошелек и категория
#     if not wallet_name or not category_name:
#         await query.edit_message_text("Ошибка: кошелек или категория не выбраны.")
#         return
#
#     # Получаем список подкатегорий
#     subcategories = get_subcategories(wallet_name, category_name)
#
#     # Проверяем, есть ли подкатегории
#     if not subcategories:
#         await query.edit_message_text(
#             f"Категория: {category_name}\nПодкатегорий нет. Добавьте новую подкатегорию:",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
#                 [InlineKeyboardButton("Назад", callback_data="back_to_category_menu")]
#             ])
#         )
#         return
#
#     # Создаем кнопки для подкатегорий
#     buttons = [[InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")] for subcat in subcategories]
#     buttons.append([InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")])
#     buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])
#
#     # Отображаем меню подкатегорий
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text(
#         f"Категория: {category_name}\nВыберите подкатегорию или добавьте новую:",
#         reply_markup=reply_markup
#     )
# async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает выбор валюты.
#     """
#     query = update.callback_query
#
#     # Симуляция доступных валют
#     available_currencies = ["USD", "EUR", "RUB", "KZT"]
#     buttons = [
#         [InlineKeyboardButton(currency, callback_data=f"currency_{currency}")]
#         for currency in available_currencies
#     ]
#     buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_subcategory_menu")])
#
#     await query.edit_message_text(
#         text="Выберите валюту:",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )
# async def add_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Запускает процесс добавления валюты в кошелек.
#     """
#     wallet_name = context.user_data.get("selected_wallet")
#
#     if not wallet_name:
#         await update.callback_query.edit_message_text("❌ Ошибка: кошелек не выбран.")
#         return
#
#     context.user_data["action"] = "add_currency"
#
#     await update.callback_query.edit_message_text("Введите название новой валюты: 💰")
#
#
#
#
# async def delete_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню удаления валюты. Если валют нет, возвращает обратно в меню валют.
#     """
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#     subcategory_name = context.user_data.get("selected_subcategory")
#
#     if not (operation_type and wallet_name and category_name and subcategory_name):
#         await query.edit_message_text("❌ Ошибка: данные для удаления валюты не выбраны.")
#         return
#
#     currencies = get_currencies(operation_type, wallet_name, category_name, subcategory_name)
#
#     # 🔥 Если валют нет, показываем сообщение и возвращаем в меню валют
#     if not currencies:
#         await query.edit_message_text(
#             "💵 Нет доступных валют для удаления.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")],
#                 [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
#             ])
#         )
#         return
#
#     # ✅ Если валюты есть, показываем кнопки для удаления
#     buttons = [[InlineKeyboardButton(currency, callback_data=f"deletecurrency_{currency}")] for currency in currencies]
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text("🗑 Выберите валюту для удаления:", reply_markup=reply_markup)
#
# async def edit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Позволяет изменить сумму, если денег не хватает.
#     """
#     await update.callback_query.edit_message_text(
#         "✏️ Введите новую сумму:",
#     )
#     context.user_data["action"] = "add_amount"  # **Перенаправляем обратно в handle_amount**
#
# async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает ввод суммы операции и не дает уйти в минус.
#     """
#     try:
#         action = context.user_data.get("action")
#         if action != "add_amount":
#             await update.message.reply_text("Ошибка: не ожидается ввод суммы. Нажмите /start, чтобы начать заново.")
#             return
#
#         amount_text = update.message.text.strip()
#         if not amount_text.isdigit():
#             await update.message.reply_text("Ошибка: сумма должна быть числом. Попробуйте снова.")
#             return
#
#         amount = float(amount_text)
#         context.user_data["amount"] = amount
#
#         # Получаем текущий баланс кошелька
#         wallet_name = context.user_data.get("selected_wallet")
#         data = load_data()
#         wallet_balance = data["wallets"].get(wallet_name, {}).get("balance", 0)
#
#         # **❌ Проверяем баланс перед расходом**
#         if context.user_data.get("operation_type") == "expense" and amount > wallet_balance:
#             await update.message.reply_text(
#                 f"⚠️ У вас недостаточно средств! Баланс: {wallet_balance}, а вы хотите потратить {amount}.",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("🔄 Вернуться в начало", callback_data="start")],
#                     [InlineKeyboardButton("✏️ Изменить сумму", callback_data="edit_amount")]
#                 ])
#             )
#             return  # ❌ **Не сохраняем сумму, если денег не хватает!**
#
#         # ✅ Продолжаем операцию
#         context.user_data.pop("action", None)
#         await update.message.reply_text("Сумма сохранена. Введите комментарий для операции.")
#         context.user_data["action"] = "add_comment"
#
#     except Exception as e:
#         logging.error(f"Ошибка в handle_amount: {e}")
#         await update.message.reply_text("Произошла ошибка при обработке суммы. Попробуйте снова.")
#
# async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает ввод комментария к операции.
#     """
#     try:
#         action = context.user_data.get("action")
#         if action != "add_comment":
#             await update.message.reply_text("Ошибка: не ожидается ввод комментария. Нажмите /start, чтобы начать заново.")
#             return
#
#         comment = update.message.text.strip()
#         context.user_data["comment"] = comment
#         context.user_data.pop("action", None)
#         await update.message.reply_text("Комментарий сохранен. Теперь отправьте фото чека.")
#
#     except Exception as e:
#         logging.error(f"Ошибка в handle_comment: {e}")
#         await update.message.reply_text("Произошла ошибка при обработке комментария. Попробуйте снова.")
#
#
# async def handle_receipt_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает документ (PDF, TXT и т. д.) и отправляет его в группу с ID чека.
#     """
#     try:
#         # Проверяем, что в сообщении есть документ
#         if not update.message.document:
#             await update.message.reply_text(
#                 "⚠️ Ошибка: в сообщении нет документа. Отправьте файл чека или нажмите 'Пропустить'.",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("⏩ Пропустить", callback_data="skip_receipt")]
#                 ]))
#             return
#
#         document = update.message.document
#         file_id = document.file_id  # ID файла
#         file_name = document.file_name  # Название файла
#         check_id = generate_check_id()  # Генерируем ID чека
#
#         # ✅ Отправляем документ в группу
#         await context.bot.send_document(
#             chat_id=GROUP_CHAT_ID,
#             document=file_id,
#             caption=f"🧾 Электронный чек `{file_name}` с ID: `{check_id}`",
#             parse_mode="Markdown"
#         )
#
#         # Сохраняем ID чека в контексте пользователя
#         context.user_data["receipt_id"] = check_id
#
#         # ✅ Показываем пользователю, что чек загружен
#         await update.message.reply_text(
#             "✅ Электронный чек загружен! Завершаем операцию...",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("💰 Показать остаток", callback_data="check_wallet_balance")],
#                 [InlineKeyboardButton("🔄 Новая операция", callback_data="start")]
#             ])
#         )
#
#         # **Вызываем сохранение операции**
#         await save_operation_and_return_to_start(update, context)
#
#     except Exception as e:
#         logging.error(f"❌ Ошибка в handle_receipt_document: {e}")
#         await update.message.reply_text("⚠️ Ошибка при обработке документа. Попробуйте снова.")
#
#
# async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает фото чека, отправляет его в группу и записывает в таблицу, затем начинает новую операцию.
#     """
#     try:
#         # Проверяем, есть ли фото в сообщении
#         if not update.message.photo:
#             await update.message.reply_text("Ошибка: в сообщении отсутствует фото. Пожалуйста, отправьте фото чека.")
#             return
#
#         photo = update.message.photo[-1]  # Берем последнюю версию фото (самое качественное)
#         file_id = photo.file_id  # ID файла фото в Telegram
#         check_id = generate_check_id()  # Генерируем уникальный ID чека
#
#         # Отправляем фото в группу с ID чека
#         await context.bot.send_photo(
#             chat_id=GROUP_CHAT_ID,
#             photo=file_id,
#             caption=f"Чек с ID: {check_id}"
#         )
#
#         # Сохраняем ID чека в контекст
#         context.user_data["receipt_id"] = check_id
#
#         # Сохраняем операцию в таблицу
#         await save_operation(context)
#
#         # Сообщаем пользователю об успешном завершении
#         await update.message.reply_text("Данные успешно сохранены. Начинаю новую операцию.")
#
#         # Очищаем контекст после завершения операции
#         context.user_data.clear()
#
#         # Возвращаем пользователя к стартовому меню
#         await start(update, context)
#     except Exception as e:
#         logging.error(f"Ошибка в handle_receipt_photo: {e}")
#         await update.message.reply_text("Произошла ошибка при обработке фото. Пожалуйста, попробуйте снова.")
#
# async def back_to_wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Возвращает в меню выбора кошелька.
#     """
#     query = update.callback_query
#     wallets = get_wallets()
#
#     # Проверяем, есть ли кошельки
#     if not wallets:
#         await query.edit_message_text("Кошельков нет. Добавьте новый кошелек.",
#                                       reply_markup=InlineKeyboardMarkup([
#                                           [InlineKeyboardButton("Добавить кошелек", callback_data="add_wallet")]
#                                       ]))
#         return
#
#     # Генерируем кнопки для кошельков
#     buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
#     buttons.append([InlineKeyboardButton("Добавить кошелек", callback_data="add_wallet")])
#
#     # Обновляем меню
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text("Выберите кошелек:", reply_markup=reply_markup)
# async def operation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обработчик выбора операции (доход или расход). После выбора показывает доступные категории.
#     """
#     query = update.callback_query
#     operation_type = "income" if query.data == "operation_income" else "expense"
#     context.user_data["operation_type"] = operation_type
#
#     wallet_name = context.user_data.get("selected_wallet")
#
#     # Загружаем соответствующие категории для выбранного кошелька и типа операции
#     categories = get_categories(operation_type, wallet_name)
#
#     if not categories:
#         await query.edit_message_text(
#             text=f"Категорий для {'дохода' if operation_type == 'income' else 'расхода'} нет.\nДобавьте новую:",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("Добавить категорию", callback_data="add_category")],
#                 [InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")]
#             ])
#         )
#         return
#
#     # Создаем кнопки для категорий
#     buttons = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
#     buttons.append([InlineKeyboardButton("Добавить категорию", callback_data="add_category")])
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")])
#
#     await query.edit_message_text(
#         text=f"Вы выбрали: {'Доход' if operation_type == 'income' else 'Расход'}.\nТеперь выберите категорию:",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )
#
#
# async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обрабатывает выбор кошелька и сразу показывает список валют."""
#     query = update.callback_query
#     wallet_name = query.data.split("_")[1]
#     context.user_data["selected_wallet"] = wallet_name
#
#     # Показываем баланс всех валют
#     await dispaly_wallet_balance(update, context)
#
#     # Спрашиваем тип операции
#     buttons = [
#         [InlineKeyboardButton("💰 Доход", callback_data="operation_income")],
#         [InlineKeyboardButton("💸 Расход", callback_data="operation_expense")],
#         [InlineKeyboardButton("🔙 Назад", callback_data="show_wallets_balance")]
#     ]
#
#     await query.edit_message_text(
#         text=f"✅ Вы выбрали кошелек: {wallet_name}\nТеперь выберите тип операции:",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )
#
# async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обработчик выбора категории.
#     """
#     query = update.callback_query
#     category_name = query.data.split("_")[1]  # Извлечение имени категории
#     wallet_name = context.user_data.get("selected_wallet")  # Кошелек из контекста
#     operation_type = context.user_data.get("operation_type")  # Тип операции из контекста
#
#     if not wallet_name or not operation_type:
#         await query.edit_message_text("Ошибка: кошелек или тип операции не выбраны.")
#         return
#
#     # Сохраняем выбранную категорию в контекст
#     context.user_data["selected_category"] = category_name
#
#     # Получаем подкатегории
#     subcategories = get_subcategories(operation_type, wallet_name, category_name)
#
#     # Генерация кнопок для подкатегорий
#     buttons = [
#         [InlineKeyboardButton(sub, callback_data=f"subcategory_{sub}")] for sub in subcategories
#     ]
#     buttons.append([InlineKeyboardButton("Добавить подкатегорию", callback_data="add_subcategory")])
#     buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])
#
#     # Отправка меню
#     await query.edit_message_text(
#         text=f"Категория: {category_name}\nВыберите подкатегорию:",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )
#
#
# async def subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает выбор подкатегории.
#     """
#     query = update.callback_query
#     subcategory_name = query.data.split("_")[1]
#     context.user_data["selected_subcategory"] = subcategory_name
#
#     # Показываем меню валют
#     await query.edit_message_text(
#         text=f"Вы выбрали подкатегорию: {subcategory_name}.\nТеперь выберите валюту:",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("Добавить валюту", callback_data="add_currency")],
#             [InlineKeyboardButton("Удалить валюту", callback_data="delete_currency")],
#             [InlineKeyboardButton("Назад", callback_data="back_to_category_menu")]
#         ])
#     )
#
#
#
# async def add_subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик добавления подкатегории."""
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#
#     if not wallet_name or not category_name:
#         await update.message.reply_text("❌ Ошибка: кошелек или категория не выбраны.")
#         return
#
#     if update.callback_query:
#         await update.callback_query.edit_message_text("Введите название новой подкатегории:")
#     else:
#         await update.message.reply_text("Введите название новой подкатегории:")
#
#     context.user_data["action"] = "add_subcategory"
#
#
#
# async def delete_subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню удаления подкатегории. Валюта остается.
#     """
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#
#     if not operation_type or not wallet_name or not category_name:
#         await query.edit_message_text("❌ Ошибка: не выбрана категория для удаления подкатегории.")
#         return
#
#     subcategories = get_subcategories(operation_type, wallet_name, category_name)
#
#     if not subcategories:
#         await query.edit_message_text(
#             "📂 Нет подкатегорий для удаления.",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
#                 [InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")]
#             ])
#         )
#         return
#
#     buttons = [[InlineKeyboardButton(subcat, callback_data=f"deletesubcat_{subcat}")] for subcat in subcategories]
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text("🗑 Выберите подкатегорию для удаления (валюта сохранится):", reply_markup=reply_markup)
#
# async def set_bot_commands(application):
#     """Устанавливает команды в меню Telegram (Bot Menu)."""
#     commands = [
#         ("update", "🔄 Обновить"),
#         ("report", "⚠️ Сообщить об ошибке ❗")
#     ]
#     await application.bot.set_my_commands(commands)
#
# def get_main_keyboard():
#     """Создаёт основную клавиатуру с кнопками."""
#     keyboard = [
#         ["🔄 Обновить", "❗ Сообщить об ошибке"]
#     ]
#     return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
# async def add_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик добавления кошелька."""
#     context.user_data["action"] = "add_wallet"
#
#     if update.callback_query:
#         await update.callback_query.message.reply_text("Введите название нового кошелька:")
#     elif update.message:
#         await update.message.reply_text("Введите название нового кошелька:")
#     else:
#         logging.error("❌ Ошибка: нет доступного сообщения для отправки запроса.")
#
# async def add_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик добавления категории."""
#     query = update.callback_query
#     wallet_name = context.user_data.get("selected_wallet")
#     operation_type = context.user_data.get("operation_type")
#
#     if not wallet_name or not operation_type:
#         await query.edit_message_text("❌ Ошибка: кошелек или тип операции не выбраны.")
#         return
#
#     context.user_data["action"] = "add_category"
#
#     await query.edit_message_text(
#         "Введите название новой категории:",
#     )
#
#
#
# async def delete_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает меню для удаления категории. Если категорий нет, возвращает обратно в меню категорий.
#     """
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#
#     if not operation_type or not wallet_name:
#         await query.edit_message_text("❌ Ошибка: кошелек или тип операции не выбраны.")
#         return
#
#     categories = get_categories(operation_type, wallet_name)
#
#     # 🔥 Если категорий нет, отправляем сообщение и сразу возвращаем в меню категорий
#     if not categories:
#         await query.edit_message_text(
#             "📂 Нет категорий для удаления.",  # ✨ Улучшил текст
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
#                 [InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")]
#             ])
#         )
#         return
#
#     # ✅ Если категории есть, показываем кнопки для удаления
#     buttons = [[InlineKeyboardButton(cat, callback_data=f"deletecat_{cat}")] for cat in categories]
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#     await query.edit_message_text("🗑 Выберите категорию для удаления:", reply_markup=reply_markup)
#
# async def confirm_delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Удаляет выбранную категорию и обновляет список категорий.
#     """
#     query = update.callback_query
#     try:
#         operation_type = context.user_data.get("operation_type")
#         wallet_name = context.user_data.get("selected_wallet")
#         category_name = query.data.split("_")[1]  # Имя категории из callback_data
#
#         # Логи для проверки данных
#         logging.info(f"Удаление категории: operation_type={operation_type}, wallet_name={wallet_name}, category_name={category_name}")
#
#         # Удаляем категорию
#         if delete_category(operation_type, wallet_name, category_name):
#             logging.info(f"Категория '{category_name}' успешно удалена.")
#             await query.edit_message_text(f"Категория '{category_name}' успешно удалена.")
#             # Обновляем меню категорий
#             await back_to_category_menu(update, context)
#         else:
#             logging.info(f"Ошибка: не удалось удалить категорию '{category_name}'.")
#             await query.edit_message_text(f"Ошибка: не удалось удалить категорию '{category_name}'.")
#     except Exception as e:
#         logging.error(f"Ошибка в confirm_delete_category: {e}")
#         if query and query.message:
#             await query.edit_message_text("Произошла ошибка при удалении категории. Попробуйте снова.")
#         else:
#             logging.error("query.message отсутствует.")
# async def send_message(update, text):
#     """
#     Универсальный метод отправки сообщений, который учитывает и текстовые, и callback-запросы.
#     """
#     if update.message:
#         await update.message.reply_text(text)
#     elif update.callback_query and update.callback_query.message:
#         await update.callback_query.message.edit_text(text)
#     else:
#         logging.error(f"❌ Ошибка: {text} не отправлено – update.message и update.callback_query отсутствуют.")
#
#
# async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает текстовые вводы, такие как создание кошелька, категории, подкатегории, сумму, комментарий и валюту.
#     """
#     try:
#         action = context.user_data.get("action")
#         if not action:
#             await update.message.reply_text("❌ Ошибка: действие не определено. Нажмите /start, чтобы начать заново.")
#             return
#
#         text = update.message.text.strip()
#         if not text:
#             await update.message.reply_text("❌ Ошибка: текст не введён. Попробуйте снова.")
#             return
#
#         logging.debug(f"📥 TEXT_HANDLER: Action = {action}, User input = {text}")
#
#         # ✅ Добавление кошелька
#         if action == "add_wallet":
#             wallet_name = f"💰 {text}"  # Добавляем смайлик кошелька
#
#             wallets = get_wallets()
#             if wallet_name in wallets:
#                 await update.message.reply_text(f"❌ Кошелёк '{wallet_name}' уже существует.")
#             else:
#                 if add_wallet(wallet_name):
#                     await update.message.reply_text(f"✅ Кошелёк '{wallet_name}' успешно добавлен!")
#                     await show_wallet_menu(update, context)  # Показываем меню
#
#                 else:
#                     await update.message.reply_text("❌ Ошибка при добавлении кошелька. Попробуйте снова.")
#
#             context.user_data.pop("action", None)
#
#         # ✅ Добавление категории
#         elif action == "add_category":
#             operation_type = context.user_data.get("operation_type")
#             wallet_name = context.user_data.get("selected_wallet")
#
#             if not operation_type or not wallet_name:
#                 await update.message.reply_text("❌ Ошибка: кошелек или тип операции не выбраны.")
#                 return
#
#             category_name = f"📂 {text}"
#
#             if add_category(operation_type, wallet_name, category_name):
#                 await update.message.reply_text(f"✅ Категория '{category_name}' успешно добавлена!")
#             else:
#                 await update.message.reply_text(f"❌ Ошибка: категория '{category_name}' уже существует.")
#
#             context.user_data.pop("action", None)
#             await show_categories(update, context)
#
#         # ✅ Добавление подкатегории
#         elif action == "add_subcategory":
#             operation_type = context.user_data.get("operation_type")
#             wallet_name = context.user_data.get("selected_wallet")
#             category_name = context.user_data.get("selected_category")
#
#             if not operation_type or not wallet_name or not category_name:
#                 await update.message.reply_text("❌ Ошибка: кошелек или категория не выбраны.")
#                 return
#
#             subcategory_name = f"🏷️ {text}"
#
#             if add_subcategory(operation_type, wallet_name, category_name, subcategory_name):
#                 await update.message.reply_text(f"✅ Подкатегория '{subcategory_name}' успешно добавлена!")
#             else:
#                 await update.message.reply_text(f"❌ Ошибка: подкатегория '{subcategory_name}' уже существует.")
#
#             context.user_data.pop("action", None)
#             await show_subcategories(update, context)
#
#         # ✅ Добавление валюты
#         elif action == "add_currency":
#             wallet_name = context.user_data.get("selected_wallet")
#
#             if not wallet_name:
#                 await update.message.reply_text("❌ Ошибка: кошелек не выбран.")
#                 return
#
#             currency_name = text.strip().upper()  # Переводим в верхний регистр
#
#             data = load_data()
#             wallet = data["wallets"].get(wallet_name, {})
#
#             # ✅ Проверяем структуру "currencies", исправляем, если не словарь
#             if "currencies" not in wallet or not isinstance(wallet["currencies"], dict):
#                 wallet["currencies"] = {}  # Должен быть словарь
#                 save_data(data)
#                 logging.warning(f"⚠ Исправлена структура 'currencies' в кошельке '{wallet_name}'.")
#
#             if currency_name in wallet["currencies"]:
#                 await update.message.reply_text(f"❌ Ошибка: валюта '{currency_name}' уже есть в кошельке.")
#                 return
#
#             wallet["currencies"][currency_name] = 0  # Создаем валюту с балансом 0
#
#             save_data(data)
#
#             logging.info(f"✅ Валюта '{currency_name}' успешно добавлена в кошелек '{wallet_name}'.")
#
#             await update.message.reply_text(f"✅ Валюта '{currency_name}' успешно добавлена в кошелек '{wallet_name}'!")
#
#             context.user_data.pop("action", None)
#
#             # 🔄 Обновляем меню валют
#             currencies = get_currencies(wallet_name)
#             buttons = [[InlineKeyboardButton(currency, callback_data=f"currency_{currency}")] for currency in currencies]
#             buttons.append([InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")])
#             buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])
#
#             reply_markup = InlineKeyboardMarkup(buttons)
#             await update.message.reply_text("💵 Выберите валюту:", reply_markup=reply_markup)
#
#         # ✅ Ввод суммы
#         elif action == "add_amount":
#             if text.lower() == "пропустить":
#                 context.user_data["amount"] = "Пропущено"
#             else:
#                 try:
#                     context.user_data["amount"] = float(text)
#                 except ValueError:
#                     await update.message.reply_text("❌ Ошибка: введите корректное число или напишите 'Пропустить'.")
#                     return
#
#             context.user_data.pop("action", None)
#             await update.message.reply_text(
#                 "✍ Введите комментарий для операции или напишите 'Пропустить':",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Пропустить", callback_data="skip_comment")]
#                 ])
#             )
#             context.user_data["action"] = "add_comment"
#
#         # ✅ Ввод комментария
#         elif action == "add_comment":
#             if text.lower() == "пропустить":
#                 context.user_data["comment"] = "Пропущено"
#             else:
#                 context.user_data["comment"] = text
#
#             context.user_data.pop("action", None)
#             await update.message.reply_text(
#                 "📸 Отправьте фото чека или напишите 'Пропустить':",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Пропустить", callback_data="skip_receipt")]
#                 ])
#             )
#             context.user_data["action"] = "upload_receipt"
#
#         else:
#             logging.warning(f"⚠️ UNKNOWN ACTION: {action}")
#             await update.message.reply_text("❌ Ошибка: неизвестное действие в тексте.")
#
#     except Exception as e:
#         logging.error(f"❌ ERROR in text_handler: {e}", exc_info=True)
#         await update.message.reply_text("⚠ Произошла непредвиденная ошибка. Попробуйте снова.")
#
# async def confirm_delete_subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Подтверждает удаление подкатегории, но валюта остается."""
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#     subcategory_name = query.data.split("_")[1]
#
#     if delete_subcategory(operation_type, wallet_name, category_name, subcategory_name):
#         await query.edit_message_text(f"✅ Подкатегория '{subcategory_name}' успешно удалена (валюта сохранена).")
#         await show_subcategories(update, context)
#     else:
#         await query.edit_message_text(f"❌ Ошибка: не удалось удалить подкатегорию '{subcategory_name}'.")
#
# async def delete_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Показывает список кошельков для удаления.
#     """
#     wallets = get_wallets()
#
#     if not wallets:
#         await update.callback_query.edit_message_text(
#             "❌ У вас пока нет кошельков. Добавьте новый:",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")]
#             ])
#         )
#         return
#
#     buttons = [[InlineKeyboardButton(wallet, callback_data=f"deletewallet_{wallet}")] for wallet in wallets]
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="start")])
#
#     await update.callback_query.edit_message_text(
#         "🗑 Выберите кошелек для удаления:",
#         reply_markup=InlineKeyboardMarkup(buttons)
#     )
# async def confirm_delete_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Подтверждает удаление выбранной валюты.
#     """
#     query = update.callback_query
#     operation_type = context.user_data.get("operation_type")
#     wallet_name = context.user_data.get("selected_wallet")
#     category_name = context.user_data.get("selected_category")
#     subcategory_name = context.user_data.get("selected_subcategory")
#     currency_name = query.data.split("_")[1]  # Получаем название валюты
#
#     # Проверяем, выбраны ли все необходимые данные
#     if not (operation_type and wallet_name and category_name and subcategory_name and currency_name):
#         await query.edit_message_text("❌ Ошибка: Данные для удаления валюты не выбраны.")
#         return
#
#     # Удаляем валюту
#     if delete_currency(operation_type, wallet_name, category_name, subcategory_name, currency_name):
#         await query.edit_message_text(f"✅ Валюта '{currency_name}' успешно удалена.")
#         await show_currency_menu(update, context)  # Обновляем меню валют
#     else:
#         await query.edit_message_text(f"❌ Ошибка: не удалось удалить валюту '{currency_name}'.")
#
#
# async def confirm_delete_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Подтверждает удаление кошелька и всех его валют.
#     """
#     query = update.callback_query
#     wallet_name = query.data.split("_")[1]
#
#     data = load_data()
#     if wallet_name not in data["wallets"]:
#         await query.edit_message_text("❌ Ошибка: Кошелек не найден или уже удален.")
#         return
#
#     del data["wallets"][wallet_name]
#     save_data(data)
#
#     await query.edit_message_text(f"✅ Кошелек '{wallet_name}' и все его валюты успешно удалены.")
#     await show_wallet_menu(update, context)
#
# async def show_wallets_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Показывает список кошельков для просмотра их баланса."""
#     data = load_data()
#     wallets = data.get("wallets", {})
#
#     if not wallets:
#         await update.callback_query.answer("❌ У вас нет кошельков. Добавьте новый!", show_alert=True)
#         return
#
#     buttons = [[InlineKeyboardButton(wallet, callback_data=f"balance_{wallet}")] for wallet in wallets]
#     buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="start")])
#
#     reply_markup = InlineKeyboardMarkup(buttons)
#
#     await update.callback_query.edit_message_text(
#         "Выберите кошелек, чтобы посмотреть его баланс:", reply_markup=reply_markup
#     )
#
# async def send_reply(update: Update, text, parse_mode=None):
#         """
#         Универсальная функция для отправки сообщений (работает и с `update.message`, и с `callback_query`).
#         """
#         try:
#             if update.message:
#                 await update.message.reply_text(text, parse_mode=parse_mode)
#             elif update.callback_query and update.callback_query.message:
#                 await update.callback_query.message.reply_text(text, parse_mode=parse_mode)
#             else:
#                 logging.error(
#                     f"❌ Ошибка отправки сообщения: {text} (update.message и update.callback_query отсутствуют).")
#         except Exception as e:
#             logging.error(f"❌ Ошибка в send_reply: {e}", exc_info=True)
#
#
# async def dispaly_wallet_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Показывает баланс кошелька со всеми валютами."""
#     try:
#         wallet_name = context.user_data.get("selected_wallet")
#
#         if not wallet_name:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id, text="❌ Ошибка: Кошелек не выбран."
#             )
#             return
#
#         # 🔥 Загружаем данные
#         data = load_data()
#         wallet = data["wallets"].get(wallet_name, {})
#
#         if "currencies" not in wallet or not wallet["currencies"]:
#             await context.bot.send_message(
#                 chat_id=update.effective_chat.id, text=f"💰 Кошелек '{wallet_name}' пока не имеет валютных счетов."
#             )
#             return
#
#         # 🔥 Формируем список балансов по валютам
#         balances_text = "\n".join(
#             [f"💵 {currency}: {balance}" for currency, balance in wallet["currencies"].items()]
#         )
#
#         await update.message.reply_text(
#             text=f"📊 *Баланс кошелька* '{wallet_name}':\n{balances_text}",
#             parse_mode="Markdown",
#             reply_markup=InlineKeyboardMarkup([
#                 [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]
#             ])
#         )
#
#     except Exception as e:
#         logging.error(f"❌ Ошибка в dispaly_wallet_balance: {e}")
#         await update.message.reply_text("❌ Ошибка при загрузке баланса. Попробуйте снова.")
#
#
# async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Главный обработчик для кнопок."""
#
#
#     query = update.callback_query
#     if "prev_menu" not in context.user_data:
#         context.user_data["prev_menu"] = []
#     try:
#         if query is None:
#             if update.message:
#                 await update.message.reply_text("❌ Ошибка: callback_query отсутствует.")
#             logging.error("❌ Ошибка: callback_query отсутствует.")
#             return
#
#
#         elif query.data == "show_wallets_balance":
#
#             await show_wallets_balance(update, context)
#
#
#         elif query.data == "check_wallet_balance":
#
#             context.user_data["checking_balance"] = True
#
#             wallets = get_wallets()
#
#             if not wallets:
#
#                 if query.message:
#
#                     await query.message.edit_text(
#
#                         "❌ У вас пока нет кошельков. Добавьте новый.",
#
#                         reply_markup=InlineKeyboardMarkup([
#
#                             [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")],
#
#                             [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]  # ✅ Кнопка возврата
#
#                         ])
#
#                     )
#
#                 else:
#
#                     await query.answer("⚠️ Ошибка: Невозможно обновить сообщение.", show_alert=True)
#
#                 return
#
#             buttons = [[InlineKeyboardButton(wallet, callback_data=f"balance_{wallet}")] for wallet in wallets]
#
#             buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")])
#
#             buttons.append([InlineKeyboardButton("🏠 В главное меню", callback_data="start")])  # ✅ Добавляем кнопку
#
#             if query.message:
#
#                 await query.message.edit_text(
#
#                     "💰 Выберите кошелек, чтобы посмотреть баланс:",
#
#                     reply_markup=InlineKeyboardMarkup(buttons)
#
#                 )
#
#             else:
#
#                 await query.answer("⚠️ Ошибка: Невозможно обновить сообщение.", show_alert=True)
#
#
#         elif query.data.startswith("balance_"):
#
#             wallet_name = query.data.split("_")[1]
#
#             context.user_data["selected_wallet"] = wallet_name  # ✅ Сохраняем выбранный кошелек
#
#             await dispaly_wallet_balance(update, context)
#
#         elif query.data == "add_wallet":
#             await add_wallet_handler(update, context)
#         elif query.data == "delete_wallet":
#             await delete_wallet_handler(update, context)
#
#         elif query.data.startswith("deletewallet_"):
#             await confirm_delete_wallet(update, context)
#         await query.answer()  # Ответ на callback, чтобы избежать таймаута Telegram
#         logging.info(f"callback_query: {query.data}")
#
#         # ✅ Выбор кошелька
#         if query.data.startswith("wallet_"):
#             context.user_data["prev_menu"].append("wallet_menu")  # Сохраняем текущий экран
#             wallet_name = query.data.split("_")[1]
#             context.user_data["selected_wallet"] = wallet_name
#
#             await query.edit_message_text(
#                 text=f"✅ Вы выбрали кошелек: {wallet_name}\nТеперь выберите тип операции:",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("💰 Доход", callback_data="operation_income")],
#                     [InlineKeyboardButton("💸 Расход", callback_data="operation_expense")],
#                     [InlineKeyboardButton("🔙 Назад", callback_data="back")]
#                 ])
#             )
#
#         # ✅ Выбор типа операции (доход/расход) → После выбора показываем категории
#         elif query.data in ["operation_expense", "operation_income"]:
#             # Сохраняем текущий экран перед переходом
#             context.user_data["prev_menu"].append("wallet_menu")
#
#             # Устанавливаем тип операции (доход или расход)
#             operation_type = "income" if query.data == "operation_income" else "expense"
#             context.user_data["operation_type"] = operation_type
#             wallet_name = context.user_data.get("selected_wallet")
#
#             categories = get_categories(operation_type, wallet_name)
#
#             if not categories:
#                 await query.edit_message_text(
#                     text=f"📂 Категорий для {'дохода' if operation_type == 'income' else 'расхода'} нет.\nДобавьте новую:",
#                     reply_markup=InlineKeyboardMarkup([
#                         [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
#                         [InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")],
#                         [InlineKeyboardButton("🔙 Назад", callback_data="back")]
#                     ])
#                 )
#                 return
#
#             # Показываем список категорий
#             await query.edit_message_text(
#                 text=f"📂 Вы выбрали: {'Доход' if operation_type == 'income' else 'Расход'}.\nТеперь выберите категорию:",
#                 reply_markup=InlineKeyboardMarkup([
#                     *[[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories],
#                     [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
#                     [InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")],
#                     [InlineKeyboardButton("🔙 Назад", callback_data="back")]
#                 ])
#             )
#
#         elif query.data == "add_category":
#             await add_category_handler(update, context)
#         elif query.data == "delete_category":
#             await delete_category_handler(update, context)
#
#         elif query.data.startswith("deletecat_"):
#             await confirm_delete_category(update, context)
#         # ✅ Выбор категории → Показываем подкатегории
#         elif query.data.startswith("category_"):
#             context.user_data["prev_menu"].append("category_menu")  # Сохраняем текущий экран
#             category_name = query.data.split("_")[1]
#             context.user_data["selected_category"] = category_name
#
#             subcategories = get_subcategories(context.user_data["operation_type"], context.user_data["selected_wallet"],
#                                               category_name)
#
#             await query.edit_message_text(
#                 text=f"🏷 Вы выбрали категорию: {category_name}.\nТеперь выберите подкатегорию:",
#                 reply_markup=InlineKeyboardMarkup([
#                     *[[InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")] for subcat in
#                       subcategories],
#                     [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
#                     [InlineKeyboardButton("🔙 Назад", callback_data="back")]
#                 ])
#             )
#
#         elif query.data == "add_subcategory":
#             await add_subcategory_handler(update, context)
#         elif query.data == "delete_subcategory":
#             await delete_subcategory_handler(update, context)
#
#         elif query.data.startswith("deletesubcat_"):
#             await confirm_delete_subcategory(update, context)
#         # ✅ Выбор подкатегории → Показываем валюту
#         elif query.data.startswith("subcategory_"):
#             context.user_data["prev_menu"].append("subcategory_menu")  # Сохраняем текущий экран
#             subcategory_name = query.data.split("_")[1]
#             context.user_data["selected_subcategory"] = subcategory_name
#
#             await show_currency_menu(update, context)
#
#         elif query.data == "add_currency":
#             await add_currency_handler(update, context)
#         elif query.data == "delete_currency":
#             await delete_currency_handler(update, context)
#
#         elif query.data.startswith("deletecurrency_"):
#             await confirm_delete_currency(update, context)
#
#         # ✅ Выбор валюты → Вводим сумму
#         elif query.data.startswith("currency_"):
#             # Сохраняем предыдущее меню перед переходом
#             context.user_data["prev_menu"].append("subcategory_menu")
#
#             currency_name = query.data.split("_")[1]
#             context.user_data["currency"] = currency_name
#
#             await query.edit_message_text(
#                 text=f"Вы выбрали валюту: {currency_name}.\nТеперь введите сумму для транзакции:",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Пропустить", callback_data="skip_amount")],
#                     [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
#                 ])
#             )
#             context.user_data["action"] = "add_amount"
#         elif query.data == "back_to_subcategory_menu":
#             await show_subcategories(update, context)  # ✅ Возвращает в подкатегории
#
#             context.user_data["action"] = "add_amount"
#
#         # ✅ Пропуск суммы → Вводим комментарий
#         elif query.data == "skip_amount":
#             context.user_data["amount"] = "Пропущено"
#             await query.edit_message_text(
#                 "Введите комментарий для операции или нажмите 'Пропустить':",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Пропустить", callback_data="skip_comment")]
#                 ])
#             )
#             context.user_data["action"] = "add_comment"
#
#         # ✅ Пропуск комментария → Отправляем чек
#         elif query.data == "skip_comment":
#             context.user_data["comment"] = "Пропущено"
#             await query.edit_message_text(
#                 "Отправьте фото чека или нажмите 'Пропустить':",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("Пропустить", callback_data="skip_receipt")]
#                 ])
#             )
#             context.user_data["action"] = "upload_receipt"
#         elif query.data == "edit_amount":
#             await edit_amount(update, context)
#
#
#         # ✅ Пропуск чека → Сохраняем операцию и показываем результат
#         elif query.data == "skip_receipt":
#             context.user_data["receipt_id"] = "Пропущено"
#             await save_operation(update,context)
#             await query.edit_message_text(
#                 "✅ Операция завершена! Что дальше?",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("🔄 Начать новую операцию", callback_data="start")]
#                 ])
#             )
#         elif query.data == "dispaly_wallet_balance":
#             await dispaly_wallet_balance(update, context)
#             await update.message.reply_text(
#                 "✅ Операция завершена! Что дальше?",
#                 reply_markup=InlineKeyboardMarkup([
#                     [InlineKeyboardButton("🔄 Новая операция", callback_data="start")]
#                 ])
#             )
#
#
#
#         elif query.data == "back":
#
#             if context.user_data["prev_menu"]:
#
#                 last_menu = context.user_data["prev_menu"].pop()  # Берем последнее меню
#
#                 if last_menu == "wallet_menu":
#
#                     await show_wallet_menu(update, context)
#
#
#                 elif last_menu == "operation_menu":
#
#                     await callback_handler(update, context)  # Показываем меню операций
#
#
#                 elif last_menu == "category_menu":
#
#                     await show_categories(update, context)
#
#
#                 elif last_menu == "subcategory_menu":
#
#                     await show_subcategories(update, context)
#
#
#                 elif last_menu == "currency_menu":
#
#                     await show_currency_menu(update, context)
#
#
#                 else:
#
#                     await show_wallet_menu(update, context)  # По умолчанию возвращаем в главное меню
#
#             else:
#
#                 await show_wallet_menu(update, context)  # Если стек пуст, вернем в главное меню
#
#
#         elif query.data == "start":
#
#             await show_wallet_menu(update, context)  # Возвращаем в главное меню
#
#
#         # ✅ Начать новую операцию → Перенаправляем в главное меню
#         elif query.data == "start":
#             await show_wallet_menu(update, context)  # ✅ Теперь возвращает корректное меню
#
#
#     except Exception as e:
#         logging.error(f"Ошибка в callback_handler: {e}")
#         await context.bot.send_message(chat_id=query.from_user.id, text="❌ Произошла ошибка. Попробуйте снова.")
#
# async def save_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Сохраняет операцию и обновляет баланс каждой валюты в кошельке отдельно.
#     """
#     try:
#         wallet_name = context.user_data.get("selected_wallet")
#         operation_type = context.user_data.get("operation_type")
#         currency = context.user_data.get("currency")
#         amount = context.user_data.get("amount")
#
#         if not wallet_name or not currency or amount is None:
#             await send_reply(update, "❌ Ошибка: данные операции не указаны.")
#             return
#
#         data = load_data()
#         wallet = data["wallets"].get(wallet_name, {})
#
#         if "currencies" not in wallet or not isinstance(wallet["currencies"], dict):
#             wallet["currencies"] = {}
#
#         if currency not in wallet["currencies"]:
#             wallet["currencies"][currency] = 0
#
#         current_balance = wallet["currencies"][currency]
#
#         if operation_type == "expense":
#             if current_balance < amount:
#                 await send_reply(update, f"❌ Недостаточно средств в {currency}! Баланс: {current_balance}")
#                 return
#             new_balance = current_balance - amount
#         else:
#             new_balance = current_balance + amount
#
#         wallet["currencies"][currency] = new_balance
#         data["wallets"][wallet_name] = wallet
#         save_data(data)
#
#         logging.info(f"✅ Баланс {currency} в кошельке '{wallet_name}' обновлен: {new_balance}")
#
#         await dispaly_wallet_balance(update, context)
#
#         context.user_data.clear()
#
#     except Exception as e:
#         logging.error(f"❌ Ошибка в save_operation: {e}", exc_info=True)
#         await send_reply(update, "❌ Ошибка при сохранении операции. Попробуйте снова.")
#
#
#
# async def save_operation_and_return_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     try:
#         # 📌 Сохраняемые данные
#         wallet_name = context.user_data.get("selected_wallet", "Не указано")
#         operation_type = context.user_data.get("operation_type", "Не указано")
#         category_name = context.user_data.get("selected_category", "Не указано")
#         subcategory_name = context.user_data.get("selected_subcategory", "Не указано")
#         currency = context.user_data.get("currency", "Не указано")
#         amount = context.user_data.get("amount", 0)
#         comment = context.user_data.get("comment", "Пропущено")
#         date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#
#         # 🛑 Логируем все данные перед сохранением
#         logging.info(f"📊 Данные для сохранения: {operation_type}, {wallet_name}, {category_name}, {subcategory_name}, {currency}, {amount}, {comment}")
#
#         # ✅ Проверяем, если сумма не число – игнорируем операцию
#         if not isinstance(amount, (int, float)) or amount <= 0:
#             await update.message.reply_text("❌ Ошибка: сумма операции должна быть положительным числом.")
#             return
#
#         # ✅ Обновляем баланс кошелька в JSON
#         data = load_data()
#         wallet = data["wallets"].get(wallet_name, {})
#
#         if "currency_balances" not in wallet:
#             wallet["currency_balances"] = {}
#
#         if currency not in wallet["currency_balances"]:
#             wallet["currency_balances"][currency] = 0
#
#         current_balance = wallet["currency_balances"][currency]
#
#         # 🔥 Обновляем баланс в зависимости от операции (доход / расход)
#         if operation_type == "expense":
#             new_balance = current_balance - amount
#         else:  # income
#             new_balance = current_balance + amount
#
#         wallet["currency_balances"][currency] = new_balance
#         data["wallets"][wallet_name] = wallet
#         save_data(data)  # ✅ Сохраняем изменения в JSON
#
#         logging.info(f"✅ Баланс {currency} в кошельке '{wallet_name}' обновлен: {new_balance}")
#
#         # ✅ Записываем в Google Sheets
#         operations_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Операции")
#         check_id = context.user_data.get("receipt_id", "Пропущено")
#         operations_sheet.append_row([
#             date, operation_type, wallet_name, category_name, subcategory_name, currency, amount, comment, check_id
#         ])
#
#         logging.info("✅ Данные успешно записаны в Google Таблицу!")
#
#         # ✅ Обновляем баланс в Telegram сразу после транзакции
#         await dispaly_wallet_balance(update, context)
#
#         # 🔄 Очищаем контекст
#         context.user_data.clear()
#
#     except Exception as e:
#         logging.error(f"❌ Ошибка при сохранении данных: {e}")
#         await update.message.reply_text("❌ Ошибка при сохранении данных. Попробуйте снова.")
#
# async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """
#     Обрабатывает отправку фото чека.
#     """
#     try:
#         # Проверяем, есть ли фото в сообщении
#         if not update.message or not update.message.photo:
#             await update.message.reply_text("Ошибка: в сообщении отсутствует фото. Пожалуйста, отправьте фото чека.")
#             return
#
#         photo = update.message.photo[-1]  # Берем последнюю (самую качественную) версию фото
#         file_id = photo.file_id  # ID файла фото в Telegram
#         check_id = generate_check_id()  # Генерируем уникальный ID чека
#
#         # Отправляем фото в группу с ID чека
#         await context.bot.send_photo(
#             chat_id=GROUP_CHAT_ID,
#             photo=file_id,
#             caption=f"Чек с ID: {check_id}"
#         )
#
#         # Сохраняем ID чека в контекст
#         context.user_data["receipt_id"] = check_id
#
#         # Вызываем метод для сохранения операции и возврата к старту
#         await save_operation_and_return_to_start(update, context)
#
#     except AttributeError as e:
#         logging.error(f"Ошибка AttributeError в photo_handler: {e}")
#         if update.message:
#             await update.message.reply_text("Ошибка при обработке фото. Попробуйте снова.")
#         else:
#             logging.error("update.message отсутствует.")
#
#     except Exception as e:
#         logging.error(f"Ошибка в photo_handler: {e}")
#         if update.message:
#             await update.message.reply_text("Произошла ошибка при обработке фото чека. Пожалуйста, попробуйте снова.")
#         else:
#             logging.error("update.message отсутствует.")
# async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обновляет главное меню."""
#     await start(update, context)
#     await update.message.reply_text("🔄 Меню обновлено!")
#
#
# async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Перенаправляет в чат для сообщений об ошибках."""
#     await update.message.reply_text(
#         "🔗 Переходите в чат для сообщения об ошибке!",
#         reply_markup=InlineKeyboardMarkup([
#             [InlineKeyboardButton("✉ Перейти в чат", url="https://t.me/mwnhn")]
#         ])
#     )
#
# def main():
#
#
#     """Запуск бота."""
#     migrate_json_structure()
#
#
#
#     application = Application.builder().token("7351753880:AAEVLbjdQp_etMQAIWp6flU-ZdjaQltVNAE").build()
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(CallbackQueryHandler(callback_handler))
#     application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
#     application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
#     application.add_handler(MessageHandler(filters.Document.ALL, handle_receipt_document))
#     # Устанавливаем команды в меню Telegram
#     # Добавляем обработчики команд
#     application.add_handler(CommandHandler("update", update_command))
#     application.add_handler(CommandHandler("report", report_command))
#     application.run_polling()
#
#
# if __name__ == "__main__":
#     main()
import asyncio
import asyncio
import asyncio
from telegram import ReplyKeyboardMarkup, KeyboardButton

import logging
import uuid
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from google_sheets import add_operation, SPREADSHEET_ID, gc
from json_manager import add_wallet, get_wallets, add_category, get_categories, add_subcategory, get_subcategories, \
    delete_wallet, delete_category, delete_subcategory, get_currencies, add_currency, delete_currency, \
    migrate_json_structure, load_data, check_balance, check_wallet_balance, update_wallet_balance, save_data

GROUP_CHAT_ID =  -1002304215716  # Замените на ваш реальный ID группы



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главное меню: показывает список кошельков + кнопки."""
    data = load_data()
    wallets = data.get("wallets", {})

    buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
    buttons.append([InlineKeyboardButton("💰 Показать баланс кошелька", callback_data="show_wallets_balance")])
    buttons.append([InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")])
    buttons.append([InlineKeyboardButton("🗑 Удалить кошелек", callback_data="delete_wallet")])

    reply_markup = InlineKeyboardMarkup(buttons)

    # ✅ **Добавляем кнопки в панель ввода сообщений (ReplyKeyboardMarkup)**

    if update.message:
        await update.message.reply_text("💰 Выберите кошелек или действие:", reply_markup=reply_markup)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text("💰 Выберите кошелек или действие:", reply_markup=reply_markup)
    else:
        logging.error("Ошибка в start(): update.callback_query.message = None")

def generate_check_id():
    """
    Генерирует уникальный ID для чека.
    """
    return str(uuid.uuid4())[:8]  # Возвращаем первые 8 символов UUID


async def show_wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    wallets = data.get("wallets", {})

    buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
    buttons.append([InlineKeyboardButton("💰 Показать баланс кошелька", callback_data="show_wallets_balance")])
    buttons.append([InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")])
    buttons.append([InlineKeyboardButton("🗑 Удалить кошелек", callback_data="delete_wallet")])

    # Добавляем обновление и сообщение об ошибке
    buttons.append([
        InlineKeyboardButton("🔄 Обновить", callback_data="refresh"),
        InlineKeyboardButton("⚠️ Сообщить об ошибке ❗", callback_data="report_issue")
    ])

    reply_markup = InlineKeyboardMarkup(buttons)

    if update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text("💰 Выберите кошелек:", reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text("💰 Выберите кошелек:", reply_markup=reply_markup)
    else:
        logging.error("Ошибка в show_wallet_menu(): update.callback_query и update.message = None")


async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню категорий для выбранного кошелька.
    """
    try:
        operation_type = context.user_data.get("operation_type")
        wallet_name = context.user_data.get("selected_wallet")

        if not operation_type or not wallet_name:
            if update.callback_query:
                await update.callback_query.edit_message_text("Ошибка: тип операции или кошелек не выбраны.")
            else:
                await update.message.reply_text("Ошибка: тип операции или кошелек не выбраны.")
            return

        categories = get_categories(operation_type, wallet_name)

        buttons = [
            [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
            [InlineKeyboardButton(" 🗑 Удалить категорию", callback_data="delete_category")],
        ]

        for category in categories:
            buttons.append([InlineKeyboardButton(category, callback_data=f"category_{category}")])

        buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")])
        reply_markup = InlineKeyboardMarkup(buttons)

        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=f"Категории для кошелька '{wallet_name}':",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text=f"Категории для кошелька '{wallet_name}':",
                reply_markup=reply_markup
            )
    except Exception as e:
        logging.error(f"Ошибка в show_categories: {e}")
        if update.callback_query:
            await update.callback_query.edit_message_text("Произошла ошибка при загрузке категорий.")
        else:
            await update.message.reply_text("Произошла ошибка при загрузке категорий.")

async def show_currency_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню выбора валюты внутри кошелька (единый список для всех категорий).
    """
    wallet_name = context.user_data.get("selected_wallet")

    if not wallet_name:
        await update.callback_query.edit_message_text("❌ Ошибка: кошелек не выбран.")
        return

    currencies = get_currencies(wallet_name)

    if not currencies:
        await update.callback_query.edit_message_text(
            "❌ В этом кошельке пока нет валют. Добавьте валюту!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
            ])
        )
        return

    buttons = [[InlineKeyboardButton(currency, callback_data=f"currency_{currency}")] for currency in currencies]
    buttons.append([InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")])
    buttons.append([InlineKeyboardButton("🗑 Удалить валюту", callback_data="delete_currency")])  # Кнопка удаления
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])

    await update.callback_query.edit_message_text("Выберите валюту:", reply_markup=InlineKeyboardMarkup(buttons))
async def show_subcategories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню подкатегорий для выбранной категории.
    """
    try:
        operation_type = context.user_data.get("operation_type")
        wallet_name = context.user_data.get("selected_wallet")
        category_name = context.user_data.get("selected_category")

        if not operation_type or not wallet_name or not category_name:
            await update.message.reply_text("Ошибка: категория больше не существует. Выберите новую.")
            return

        # Проверяем, существует ли категория
        categories = get_categories(operation_type, wallet_name)
        if category_name not in categories:
            await update.message.reply_text("Ошибка: выбранная категория была удалена. Выберите новую.")
            await back_to_category_menu(update, context)
            return

        # Получаем подкатегории
        subcategories = get_subcategories(operation_type, wallet_name, category_name)

        # Создаём кнопки подкатегорий
        buttons = [
            [InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")]
            for subcat in subcategories
        ]
        buttons.append([InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")])
        buttons.append([InlineKeyboardButton("🗑 Удалить подкатегорию", callback_data="delete_subcategory")])  # Кнопка удаления
        buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])

        reply_markup = InlineKeyboardMarkup(buttons)

        # Отправляем меню
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=f"Категория: {category_name}\nВыберите подкатегорию:",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                text=f"Категория: {category_name}\nВыберите подкатегорию:",
                reply_markup=reply_markup
            )
    except Exception as e:
        logging.error(f"Ошибка в show_subcategories: {e}")
        await update.message.reply_text("Произошла ошибка при загрузке подкатегорий. Попробуйте снова.")

async def back_to_category_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Возвращает пользователя в меню категорий.
    """
    query = update.callback_query
    operation_type = context.user_data.get("operation_type")
    wallet_name = context.user_data.get("selected_wallet")

    # Проверяем, выбраны ли тип операции и кошелек
    if not operation_type or not wallet_name:
        await query.edit_message_text("Ошибка: тип операции или кошелек не выбраны.")
        return

    # Получаем обновленный список категорий
    categories = get_categories(operation_type, wallet_name)

    # Проверяем, есть ли категории
    if not categories:
        await query.edit_message_text("Категорий нет. Добавьте новую категорию.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
                                          [InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")]
                                      ]))
        return

    # Создаем кнопки для категорий
    buttons = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
    buttons.append([InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")])
    buttons.append([InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")])
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_wallet_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("Выберите категорию:", reply_markup=reply_markup)

async def back_to_subcategory_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Возвращает пользователя в меню подкатегорий.
    """
    query = update.callback_query
    wallet_name = context.user_data.get("selected_wallet")
    category_name = context.user_data.get("selected_category")

    # Проверяем, выбраны ли кошелек и категория
    if not wallet_name or not category_name:
        await query.edit_message_text("Ошибка: кошелек или категория не выбраны.")
        return

    # Получаем список подкатегорий
    subcategories = get_subcategories(wallet_name, category_name)

    # Проверяем, есть ли подкатегории
    if not subcategories:
        await query.edit_message_text(
            f"Категория: {category_name}\nПодкатегорий нет. Добавьте новую подкатегорию:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
                [InlineKeyboardButton("Назад", callback_data="back_to_category_menu")]
            ])
        )
        return

    # Создаем кнопки для подкатегорий
    buttons = [[InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")] for subcat in subcategories]
    buttons.append([InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")])
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])

    # Отображаем меню подкатегорий
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text(
        f"Категория: {category_name}\nВыберите подкатегорию или добавьте новую:",
        reply_markup=reply_markup
    )
async def currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает выбор валюты.
    """
    query = update.callback_query

    # Симуляция доступных валют
    available_currencies = ["USD", "EUR", "RUB", "KZT"]
    buttons = [
        [InlineKeyboardButton(currency, callback_data=f"currency_{currency}")]
        for currency in available_currencies
    ]
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_subcategory_menu")])

    await query.edit_message_text(
        text="Выберите валюту:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def add_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запускает процесс добавления валюты в кошелек.
    """
    wallet_name = context.user_data.get("selected_wallet")

    if not wallet_name:
        await update.callback_query.edit_message_text("❌ Ошибка: кошелек не выбран.")
        return

    context.user_data["action"] = "add_currency"

    await update.callback_query.edit_message_text("Введите название новой валюты: 💰")




async def delete_currency_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню удаления валюты. Если валют нет, возвращает обратно в меню валют.
    """
    query = update.callback_query
    wallet_name = context.user_data.get("selected_wallet")

    if not wallet_name:
        await query.edit_message_text("❌ Ошибка: кошелек не выбран.")
        return

    currencies = get_currencies(wallet_name)

    # 🔥 Если валют нет, показываем сообщение и возвращаем в меню валют
    if not currencies:
        await query.edit_message_text(
            "💵 Нет доступных валют для удаления.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
            ])
        )
        return

    # ✅ Если валюты есть, показываем кнопки для удаления
    buttons = [[InlineKeyboardButton(currency, callback_data=f"deletecurrency_{currency}")] for currency in currencies]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("🗑 Выберите валюту для удаления:", reply_markup=reply_markup)

async def edit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Позволяет изменить сумму, если денег не хватает.
    """
    await update.callback_query.edit_message_text(
        "✏️ Введите новую сумму:",
    )
    context.user_data["action"] = "add_amount"  # **Перенаправляем обратно в handle_amount**

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает ввод суммы операции и не дает уйти в минус.
    """
    try:
        action = context.user_data.get("action")
        if action != "add_amount":
            await update.message.reply_text("Ошибка: не ожидается ввод суммы. Нажмите /start, чтобы начать заново.")
            return

        amount_text = update.message.text.strip()
        if not amount_text.isdigit():
            await update.message.reply_text("Ошибка: сумма должна быть числом. Попробуйте снова.")
            return

        amount = float(amount_text)
        context.user_data["amount"] = amount

        # Получаем текущий баланс кошелька
        wallet_name = context.user_data.get("selected_wallet")
        data = load_data()
        wallet_balance = data["wallets"].get(wallet_name, {}).get("balance", 0)

        # **❌ Проверяем баланс перед расходом**
        if context.user_data.get("operation_type") == "expense" and amount > wallet_balance:
            await update.message.reply_text(
                f"⚠️ У вас недостаточно средств! Баланс: {wallet_balance}, а вы хотите потратить {amount}.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Вернуться в начало", callback_data="start")],
                    [InlineKeyboardButton("✏️ Изменить сумму", callback_data="edit_amount")]
                ])
            )
            return  # ❌ **Не сохраняем сумму, если денег не хватает!**

        # ✅ Продолжаем операцию
        context.user_data.pop("action", None)
        await update.message.reply_text("Сумма сохранена. Введите комментарий для операции.")
        context.user_data["action"] = "add_comment"

    except Exception as e:
        logging.error(f"Ошибка в handle_amount: {e}")
        await update.message.reply_text("Произошла ошибка при обработке суммы. Попробуйте снова.")

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает ввод комментария к операции.
    """
    try:
        action = context.user_data.get("action")
        if action != "add_comment":
            await update.message.reply_text("Ошибка: не ожидается ввод комментария. Нажмите /start, чтобы начать заново.")
            return

        comment = update.message.text.strip()
        context.user_data["comment"] = comment
        context.user_data.pop("action", None)
        await update.message.reply_text("Комментарий сохранен. Теперь отправьте фото чека.")

    except Exception as e:
        logging.error(f"Ошибка в handle_comment: {e}")
        await update.message.reply_text("Произошла ошибка при обработке комментария. Попробуйте снова.")


async def handle_receipt_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает документ (PDF, TXT и т. д.) и отправляет его в группу с ID чека.
    """
    try:
        if not update.message.document:
            await update.message.reply_text(
                "⚠️ Ошибка: в сообщении нет документа. Отправьте файл чека или нажмите 'Пропустить'.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⏩ Пропустить", callback_data="skip_receipt")]
                ]))
            return

        document = update.message.document
        file_id = document.file_id  # ID файла
        file_name = document.file_name  # Название файла
        check_id = generate_check_id()  # Генерируем уникальный ID чека

        # ✅ Отправляем документ в группу
        await context.bot.send_document(
            chat_id=GROUP_CHAT_ID,
            document=file_id,
            caption=f"🧾 Электронный чек `{file_name}` с ID: `{check_id}`",
            parse_mode="Markdown"
        )

        # ✅ Сохраняем ID чека в контексте пользователя
        context.user_data["receipt_id"] = check_id

        # ✅ Проверяем, есть ли сумма в контексте перед сохранением
        if "amount" not in context.user_data or context.user_data["amount"] is None:
            await update.message.reply_text("❌ Ошибка: сумма не сохранена. Попробуйте снова.")
            return

        # ✅ Вызываем сохранение операции с правильными аргументами
        await save_operation_and_return_to_start(update, context)

    except Exception as e:
        logging.error(f"❌ Ошибка в handle_receipt_document: {e}")
        await update.message.reply_text("⚠️ Ошибка при обработке документа. Попробуйте снова.")

async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает фото чека, отправляет его в группу и записывает в таблицу, затем начинает новую операцию.
    """
    try:
        if not update.message.photo:
            await update.message.reply_text("Ошибка: в сообщении отсутствует фото. Пожалуйста, отправьте фото чека.")
            return

        photo = update.message.photo[-1]  # Берем последнюю версию фото (самое качественное)
        file_id = photo.file_id  # ID файла фото в Telegram
        check_id = generate_check_id()  # Генерируем уникальный ID чека

        # Отправляем фото в группу с ID чека
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=file_id,
            caption=f"Чек с ID: {check_id}"
        )

        # ✅ Сохраняем ID чека в контекст
        context.user_data["receipt_id"] = check_id

        # ✅ Проверяем, есть ли сумма перед сохранением
        if "amount" not in context.user_data or context.user_data["amount"] is None:
            await update.message.reply_text("❌ Ошибка: сумма не сохранена. Попробуйте снова.")
            return

        # **Вызываем сохранение операции с правильными аргументами**
        await save_operation_and_return_to_start(update, context)

    except Exception as e:
        logging.error(f"Ошибка в handle_receipt_photo: {e}")
        await update.message.reply_text(f"Произошла ошибка при обработке фото: {e}. Пожалуйста, попробуйте снова.")

async def back_to_wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Возвращает в меню выбора кошелька.
    """
    query = update.callback_query
    wallets = get_wallets()

    # Проверяем, есть ли кошельки
    if not wallets:
        await query.edit_message_text("Кошельков нет. Добавьте новый кошелек.",
                                      reply_markup=InlineKeyboardMarkup([
                                          [InlineKeyboardButton("Добавить кошелек", callback_data="add_wallet")]
                                      ]))
        return

    # Генерируем кнопки для кошельков
    buttons = [[InlineKeyboardButton(wallet, callback_data=f"wallet_{wallet}")] for wallet in wallets]
    buttons.append([InlineKeyboardButton("Добавить кошелек", callback_data="add_wallet")])

    # Обновляем меню
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("Выберите кошелек:", reply_markup=reply_markup)
async def operation_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора операции (доход или расход). После выбора показывает доступные категории.
    """
    query = update.callback_query
    operation_type = "income" if query.data == "operation_income" else "expense"
    context.user_data["operation_type"] = operation_type

    wallet_name = context.user_data.get("selected_wallet")

    # Загружаем соответствующие категории для выбранного кошелька и типа операции
    categories = get_categories(operation_type, wallet_name)

    if not categories:
        await query.edit_message_text(
            text=f"Категорий для {'дохода' if operation_type == 'income' else 'расхода'} нет.\nДобавьте новую:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Добавить категорию", callback_data="add_category")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")]
            ])
        )
        return

    # Создаем кнопки для категорий
    buttons = [[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories]
    buttons.append([InlineKeyboardButton("Добавить категорию", callback_data="add_category")])
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")])

    await query.edit_message_text(
        text=f"Вы выбрали: {'Доход' if operation_type == 'income' else 'Расход'}.\nТеперь выберите категорию:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор кошелька и предлагает выбрать тип операции (доход/расход)."""
    query = update.callback_query
    wallet_name = query.data.split("_")[1]

    # Сохраняем выбранный кошелек
    context.user_data["selected_wallet"] = wallet_name

    # Спрашиваем тип операции
    buttons = [
        [InlineKeyboardButton("💰 Доход", callback_data="operation_income")],
        [InlineKeyboardButton("💸 Расход", callback_data="operation_expense")],
        [InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")]
    ]

    await query.edit_message_text(
        text=f"✅ Вы выбрали кошелек: {wallet_name}\nТеперь выберите тип операции:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик выбора категории.
    """
    query = update.callback_query
    category_name = query.data.split("_")[1]  # Извлечение имени категории
    wallet_name = context.user_data.get("selected_wallet")  # Кошелек из контекста
    operation_type = context.user_data.get("operation_type")  # Тип операции из контекста

    if not wallet_name or not operation_type:
        await query.edit_message_text("Ошибка: кошелек или тип операции не выбраны.")
        return

    # Сохраняем выбранную категорию в контекст
    context.user_data["selected_category"] = category_name

    # Получаем подкатегории
    subcategories = get_subcategories(operation_type, wallet_name, category_name)

    # Генерация кнопок для подкатегорий
    buttons = [
        [InlineKeyboardButton(sub, callback_data=f"subcategory_{sub}")] for sub in subcategories
    ]
    buttons.append([InlineKeyboardButton("Добавить подкатегорию", callback_data="add_subcategory")])
    buttons.append([InlineKeyboardButton("Назад", callback_data="back_to_category_menu")])

    # Отправка меню
    await query.edit_message_text(
        text=f"Категория: {category_name}\nВыберите подкатегорию:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает выбор подкатегории.
    """
    query = update.callback_query
    subcategory_name = query.data.split("_")[1]
    context.user_data["selected_subcategory"] = subcategory_name

    # Показываем меню валют
    await query.edit_message_text(
        text=f"Вы выбрали подкатегорию: {subcategory_name}.\nТеперь выберите валюту:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Добавить валюту", callback_data="add_currency")],
            [InlineKeyboardButton("Удалить валюту", callback_data="delete_currency")],
            [InlineKeyboardButton("Назад", callback_data="back_to_category_menu")]
        ])
    )



async def add_subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик добавления подкатегории."""
    wallet_name = context.user_data.get("selected_wallet")
    category_name = context.user_data.get("selected_category")

    if not wallet_name or not category_name:
        await update.message.reply_text("❌ Ошибка: кошелек или категория не выбраны.")
        return

    if update.callback_query:
        await update.callback_query.edit_message_text("Введите название новой подкатегории:")
    else:
        await update.message.reply_text("Введите название новой подкатегории:")

    context.user_data["action"] = "add_subcategory"



async def delete_subcategory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню удаления подкатегории. Валюта остается.
    """
    query = update.callback_query
    operation_type = context.user_data.get("operation_type")
    wallet_name = context.user_data.get("selected_wallet")
    category_name = context.user_data.get("selected_category")

    if not operation_type or not wallet_name or not category_name:
        await query.edit_message_text("❌ Ошибка: не выбрана категория для удаления подкатегории.")
        return

    subcategories = get_subcategories(operation_type, wallet_name, category_name)

    if not subcategories:
        await query.edit_message_text(
            "📂 Нет подкатегорий для удаления.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")]
            ])
        )
        return

    buttons = [[InlineKeyboardButton(subcat, callback_data=f"deletesubcat_{subcat}")] for subcat in subcategories]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("🗑 Выберите подкатегорию для удаления (валюта сохранится):", reply_markup=reply_markup)

async def set_bot_commands(application):
    """Устанавливает команды в меню Telegram (Bot Menu)."""
    commands = [
        ("update", "🔄 Обновить"),
        ("report", "⚠️ Сообщить об ошибке ❗")
    ]
    await application.bot.set_my_commands(commands)

def get_main_keyboard():
    """Создаёт основную клавиатуру с кнопками."""
    keyboard = [
        ["🔄 Обновить", "❗ Сообщить об ошибке"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
async def add_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик добавления кошелька."""
    context.user_data["action"] = "add_wallet"

    if update.callback_query:
        await update.callback_query.message.reply_text("Введите название нового кошелька:")
    elif update.message:
        await update.message.reply_text("Введите название нового кошелька:")
    else:
        logging.error("❌ Ошибка: нет доступного сообщения для отправки запроса.")

async def add_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик добавления категории."""
    query = update.callback_query
    wallet_name = context.user_data.get("selected_wallet")
    operation_type = context.user_data.get("operation_type")

    if not wallet_name or not operation_type:
        await query.edit_message_text("❌ Ошибка: кошелек или тип операции не выбраны.")
        return

    context.user_data["action"] = "add_category"

    await query.edit_message_text(
        "Введите название новой категории:",
    )



async def delete_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает меню для удаления категории. Если категорий нет, возвращает обратно в меню категорий.
    """
    query = update.callback_query
    operation_type = context.user_data.get("operation_type")
    wallet_name = context.user_data.get("selected_wallet")

    if not operation_type or not wallet_name:
        await query.edit_message_text("❌ Ошибка: кошелек или тип операции не выбраны.")
        return

    categories = get_categories(operation_type, wallet_name)

    # 🔥 Если категорий нет, отправляем сообщение и сразу возвращаем в меню категорий
    if not categories:
        await query.edit_message_text(
            "📂 Нет категорий для удаления.",  # ✨ Улучшил текст
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
                [InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")]
            ])
        )
        return

    # ✅ Если категории есть, показываем кнопки для удаления
    buttons = [[InlineKeyboardButton(cat, callback_data=f"deletecat_{cat}")] for cat in categories]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_category_menu")])

    reply_markup = InlineKeyboardMarkup(buttons)
    await query.edit_message_text("🗑 Выберите категорию для удаления:", reply_markup=reply_markup)

async def confirm_delete_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Удаляет выбранную категорию и обновляет список категорий.
    """
    query = update.callback_query
    try:
        operation_type = context.user_data.get("operation_type")
        wallet_name = context.user_data.get("selected_wallet")
        category_name = query.data.split("_")[1]  # Имя категории из callback_data

        # Логи для проверки данных
        logging.info(f"Удаление категории: operation_type={operation_type}, wallet_name={wallet_name}, category_name={category_name}")

        # Удаляем категорию
        if delete_category(operation_type, wallet_name, category_name):
            logging.info(f"Категория '{category_name}' успешно удалена.")
            await query.edit_message_text(f"Категория '{category_name}' успешно удалена.")
            # Обновляем меню категорий
            await back_to_category_menu(update, context)
        else:
            logging.info(f"Ошибка: не удалось удалить категорию '{category_name}'.")
            await query.edit_message_text(f"Ошибка: не удалось удалить категорию '{category_name}'.")
    except Exception as e:
        logging.error(f"Ошибка в confirm_delete_category: {e}")
        if query and query.message:
            await query.edit_message_text("Произошла ошибка при удалении категории. Попробуйте снова.")
        else:
            logging.error("query.message отсутствует.")
async def send_message(update, text):
    """
    Универсальный метод отправки сообщений, который учитывает и текстовые, и callback-запросы.
    """
    if update.message:
        await update.message.reply_text(text)
    elif update.callback_query and update.callback_query.message:
        await update.callback_query.message.edit_text(text)
    else:
        logging.error(f"❌ Ошибка: {text} не отправлено – update.message и update.callback_query отсутствуют.")


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает текстовые вводы, такие как создание кошелька, категории, подкатегории, сумму, комментарий и валюту.
    """
    try:
        action = context.user_data.get("action")
        if not action:
            await update.message.reply_text("❌ Ошибка: действие не определено. Нажмите /start, чтобы начать заново.")
            return

        text = update.message.text.strip()
        if not text:
            await update.message.reply_text("❌ Ошибка: текст не введён. Попробуйте снова.")
            return

        # ✅ Добавление кошелька
        # ✅ Добавление кошелька
        if action == "add_wallet":
            wallet_name = f"💰 {text}"  # Добавляем смайлик кошелька

            wallets = get_wallets()
            if wallet_name in wallets:
                await update.message.reply_text(f"❌ Кошелёк '{wallet_name}' уже существует.")
            else:
                if add_wallet(wallet_name):
                    await update.message.reply_text(f"✅ Кошелёк '{wallet_name}' успешно добавлен!")

                    # 🔥 Теперь просто вызываем show_wallet_menu, чтобы показать меню
                    await show_wallet_menu(update, context)

                else:
                    await update.message.reply_text("❌ Ошибка при добавлении кошелька. Попробуйте снова.")

            context.user_data.pop("action", None)


        # ✅ Добавление категории → После добавления вызываем меню категорий
        elif action == "add_category":
            operation_type = context.user_data.get("operation_type")
            wallet_name = context.user_data.get("selected_wallet")

            if not operation_type or not wallet_name:
                await update.message.reply_text("❌ Ошибка: кошелек или тип операции не выбраны.")
                return

            category_name = f"📂 {text}"  # Добавляем смайлик категории

            if add_category(operation_type, wallet_name, category_name):
                await update.message.reply_text(f"✅ Категория '{category_name}' успешно добавлена!")
            else:
                await update.message.reply_text(f"❌ Ошибка: категория '{category_name}' уже существует.")

            context.user_data.pop("action", None)
            await show_categories(update, context)

        # ✅ Добавление подкатегории → После добавления вызываем меню подкатегорий
        elif action == "add_subcategory":
            operation_type = context.user_data.get("operation_type")
            wallet_name = context.user_data.get("selected_wallet")
            category_name = context.user_data.get("selected_category")

            if not operation_type or not wallet_name or not category_name:
                await update.message.reply_text("❌ Ошибка: кошелек или категория не выбраны.")
                return

            subcategory_name = f"🏷️ {text}"  # Добавляем смайлик подкатегории

            if add_subcategory(operation_type, wallet_name, category_name, subcategory_name):
                await update.message.reply_text(f"✅ Подкатегория '{subcategory_name}' успешно добавлена!")
            else:
                await update.message.reply_text(f"❌ Ошибка: подкатегория '{subcategory_name}' уже существует.")

            context.user_data.pop("action", None)
            await show_subcategories(update, context)

        # ✅ Добавление валюты → После добавления вызываем меню валют
        elif action == "add_currency":
            wallet_name = context.user_data.get("selected_wallet")

            if not wallet_name:
                await update.message.reply_text("❌ Ошибка: кошелек не выбран.")
                return

            currency_name = text.strip().upper()  # Форматируем валюту в верхний регистр

            data = load_data()
            wallet = data["wallets"].get(wallet_name, {})

            if "currencies" not in wallet or not isinstance(wallet["currencies"], dict):
                wallet["currencies"] = {}  # Исправляем структуру, если там что-то не так

            if currency_name in wallet["currencies"]:
                await update.message.reply_text(f"❌ Ошибка: валюта '{currency_name}' уже есть в кошельке.")
                return

            wallet["currencies"][currency_name] = 0  # Создаем новую валюту с балансом 0
            data["wallets"][wallet_name] = wallet
            save_data(data)

            await update.message.reply_text(f"✅ Валюта '{currency_name}' успешно добавлена в кошелек '{wallet_name}'!")

            context.user_data.pop("action", None)

            # 🔄 Возвращаем пользователя в меню выбора валюты
            currencies = get_currencies(wallet_name)

            buttons = [[InlineKeyboardButton(currency, callback_data=f"currency_{currency}")] for currency in
                       currencies]
            buttons.append([InlineKeyboardButton("➕ Добавить валюту", callback_data="add_currency")])
            buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")])

            reply_markup = InlineKeyboardMarkup(buttons)

            await update.message.reply_text("💵 Выберите валюту:", reply_markup=reply_markup)



        # ✅ Ввод суммы → После суммы вводим комментарий
        elif action == "add_amount":
            if text.lower() == "пропустить":
                context.user_data["amount"] = "Пропущено"
            else:
                try:
                    context.user_data["amount"] = float(text)
                except ValueError:
                    await update.message.reply_text("❌ Ошибка: введите корректное число или напишите 'Пропустить'.")
                    return

            context.user_data.pop("action", None)
            await update.message.reply_text(
                "✍ Введите комментарий для операции или напишите 'Пропустить':",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Пропустить", callback_data="skip_comment")]
                ])
            )
            context.user_data["action"] = "add_comment"

        # ✅ Ввод комментария → После комментария загружаем чек
        elif action == "add_comment":
            if text.lower() == "пропустить":
                context.user_data["comment"] = "Пропущено"
            else:
                context.user_data["comment"] = text

            context.user_data.pop("action", None)
            await update.message.reply_text(
                "📸 Отправьте фото чека или напишите 'Пропустить':",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Пропустить", callback_data="skip_receipt")]
                ])
            )
            context.user_data["action"] = "upload_receipt"

        else:
            await update.message.reply_text("❌ Ошибка: неизвестное действие в тексте.")

    except Exception as e:
        logging.error(f"❌ Ошибка в text_handler: {e}")
        await update.message.reply_text(f"❌ Произошла ошибка: {e}. Попробуйте снова.")

async def confirm_delete_subcategory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждает удаление подкатегории, но валюта остается."""
    query = update.callback_query
    operation_type = context.user_data.get("operation_type")
    wallet_name = context.user_data.get("selected_wallet")
    category_name = context.user_data.get("selected_category")
    subcategory_name = query.data.split("_")[1]

    if delete_subcategory(operation_type, wallet_name, category_name, subcategory_name):
        await query.edit_message_text(f"✅ Подкатегория '{subcategory_name}' успешно удалена (валюта сохранена).")
        await show_subcategories(update, context)
    else:
        await query.edit_message_text(f"❌ Ошибка: не удалось удалить подкатегорию '{subcategory_name}'.")

async def delete_wallet_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Показывает список кошельков для удаления.
    """
    wallets = get_wallets()

    if not wallets:
        await update.callback_query.edit_message_text(
            "❌ У вас пока нет кошельков. Добавьте новый:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")]
            ])
        )
        return

    buttons = [[InlineKeyboardButton(wallet, callback_data=f"deletewallet_{wallet}")] for wallet in wallets]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="start")])

    await update.callback_query.edit_message_text(
        "🗑 Выберите кошелек для удаления:",
        reply_markup=InlineKeyboardMarkup(buttons)
    )
async def confirm_delete_currency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подтверждает удаление выбранной валюты.
    """
    query = update.callback_query
    wallet_name = context.user_data.get("selected_wallet")
    currency_name = query.data.split("_")[1]  # Получаем название валюты

    # Проверяем, выбраны ли все необходимые данные
    if not wallet_name or not currency_name:
        await query.edit_message_text("❌ Ошибка: Данные для удаления валюты не выбраны.")
        return

    # Загружаем данные
    data = load_data()
    wallet = data["wallets"].get(wallet_name, {})

    if "currencies" not in wallet or currency_name not in wallet["currencies"]:
        await query.edit_message_text(f"❌ Ошибка: валюта '{currency_name}' не найдена в кошельке.")
        return

    # Удаляем валюту
    del wallet["currencies"][currency_name]
    data["wallets"][wallet_name] = wallet
    save_data(data)  # Сохраняем изменения

    await query.edit_message_text(f"✅ Валюта '{currency_name}' успешно удалена.")

    # 🔄 Возвращаем пользователя в меню выбора валюты
    await show_currency_menu(update, context)

async def confirm_delete_wallet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Подтверждает удаление кошелька и всех его валют.
    """
    query = update.callback_query
    wallet_name = query.data.split("_")[1]

    data = load_data()
    if wallet_name not in data["wallets"]:
        await query.edit_message_text("❌ Ошибка: Кошелек не найден или уже удален.")
        return

    del data["wallets"][wallet_name]
    save_data(data)

    await query.edit_message_text(f"✅ Кошелек '{wallet_name}' и все его валюты успешно удалены.")
    await show_wallet_menu(update, context)

async def show_wallets_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает список кошельков для просмотра их баланса."""
    data = load_data()
    wallets = data.get("wallets", {})

    if not wallets:
        await update.callback_query.answer("❌ У вас нет кошельков. Добавьте новый!", show_alert=True)
        return

    buttons = [[InlineKeyboardButton(wallet, callback_data=f"balance_{wallet}")] for wallet in wallets]
    buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="start")])

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.callback_query.edit_message_text(
        "Выберите кошелек, чтобы посмотреть его баланс:", reply_markup=reply_markup
    )

async def dispaly_wallet_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает баланс кошелька с отдельными валютами."""
    try:
        wallet_name = context.user_data.get("selected_wallet")

        if not wallet_name:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="❌ Ошибка: Кошелек не выбран."
            )
            return

        # 🔥 Загружаем данные
        data = load_data()
        wallet = data["wallets"].get(wallet_name, {})

        if "currencies" not in wallet or not wallet["currencies"]:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"💰 Кошелек '{wallet_name}' пока не имеет валютных счетов."
            )
            return

        # 🔥 Формируем список балансов по валютам (все валюты в кошельке)
        balances_text = "\n".join(
            [f"💵 {currency}: {balance}" for currency, balance in wallet["currencies"].items()]
        )

        if update.message:
            await update.message.reply_text(
                text=f"📊 *Баланс кошелька* '{wallet_name}':\n{balances_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Обновить", callback_data="check_wallet_balance")],
                    [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]
                ])
            )
        elif update.callback_query:
            await update.callback_query.message.edit_text(
                text=f"📊 *Баланс кошелька* '{wallet_name}':\n{balances_text}",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Обновить", callback_data="check_wallet_balance")],
                    [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]
                ])
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=f"📊 *Баланс кошелька* '{wallet_name}':\n{balances_text}",
                parse_mode="Markdown"
            )

    except Exception as e:
        logging.error(f"❌ Ошибка в dispaly_wallet_balance: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="❌ Ошибка при загрузке баланса. Попробуйте снова."
        )


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Главный обработчик для кнопок."""


    query = update.callback_query
    if "prev_menu" not in context.user_data:
        context.user_data["prev_menu"] = []
    try:
        if query is None:
            if update.message:
                await update.message.reply_text("❌ Ошибка: callback_query отсутствует.")
            logging.error("❌ Ошибка: callback_query отсутствует.")
            return


        elif query.data == "show_wallets_balance":

            await show_wallets_balance(update, context)


        elif query.data == "check_wallet_balance":

            context.user_data["checking_balance"] = True

            wallets = get_wallets()

            if not wallets:

                if query.message:

                    await query.message.edit_text(

                        "❌ У вас пока нет кошельков. Добавьте новый.",

                        reply_markup=InlineKeyboardMarkup([

                            [InlineKeyboardButton("➕ Добавить кошелек", callback_data="add_wallet")],

                            [InlineKeyboardButton("🏠 В главное меню", callback_data="start")]  # ✅ Кнопка возврата

                        ])

                    )

                else:

                    await query.answer("⚠️ Ошибка: Невозможно обновить сообщение.", show_alert=True)

                return

            buttons = [[InlineKeyboardButton(wallet, callback_data=f"balance_{wallet}")] for wallet in wallets]

            buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_wallet_menu")])

            buttons.append([InlineKeyboardButton("🏠 В главное меню", callback_data="start")])  # ✅ Добавляем кнопку

            if query.message:

                await query.message.edit_text(

                    "💰 Выберите кошелек, чтобы посмотреть баланс:",

                    reply_markup=InlineKeyboardMarkup(buttons)

                )

            else:

                await query.answer("⚠️ Ошибка: Невозможно обновить сообщение.", show_alert=True)


        elif query.data.startswith("balance_"):

            wallet_name = query.data.split("_")[1]

            context.user_data["selected_wallet"] = wallet_name  # ✅ Сохраняем выбранный кошелек

            await dispaly_wallet_balance(update, context)

        elif query.data == "add_wallet":
            await add_wallet_handler(update, context)
        elif query.data == "delete_wallet":
            await delete_wallet_handler(update, context)

        elif query.data.startswith("deletewallet_"):
            await confirm_delete_wallet(update, context)
        await query.answer()  # Ответ на callback, чтобы избежать таймаута Telegram
        logging.info(f"callback_query: {query.data}")

        # ✅ Выбор кошелька
        if query.data.startswith("wallet_"):
            context.user_data["prev_menu"].append("wallet_menu")  # Сохраняем текущий экран
            wallet_name = query.data.split("_")[1]
            context.user_data["selected_wallet"] = wallet_name

            await query.edit_message_text(
                text=f"✅ Вы выбрали кошелек: {wallet_name}\nТеперь выберите тип операции:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 Доход", callback_data="operation_income")],
                    [InlineKeyboardButton("💸 Расход", callback_data="operation_expense")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back")]
                ])
            )

        # ✅ Выбор типа операции (доход/расход) → После выбора показываем категории
        elif query.data in ["operation_expense", "operation_income"]:
            # Сохраняем текущий экран перед переходом
            context.user_data["prev_menu"].append("wallet_menu")

            # Устанавливаем тип операции (доход или расход)
            operation_type = "income" if query.data == "operation_income" else "expense"
            context.user_data["operation_type"] = operation_type
            wallet_name = context.user_data.get("selected_wallet")

            categories = get_categories(operation_type, wallet_name)

            if not categories:
                await query.edit_message_text(
                    text=f"📂 Категорий для {'дохода' if operation_type == 'income' else 'расхода'} нет.\nДобавьте новую:",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
                        [InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")],
                        [InlineKeyboardButton("🔙 Назад", callback_data="back")]
                    ])
                )
                return

            # Показываем список категорий
            await query.edit_message_text(
                text=f"📂 Вы выбрали: {'Доход' if operation_type == 'income' else 'Расход'}.\nТеперь выберите категорию:",
                reply_markup=InlineKeyboardMarkup([
                    *[[InlineKeyboardButton(cat, callback_data=f"category_{cat}")] for cat in categories],
                    [InlineKeyboardButton("➕ Добавить категорию", callback_data="add_category")],
                    [InlineKeyboardButton("🗑 Удалить категорию", callback_data="delete_category")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back")]
                ])
            )

        elif query.data == "add_category":
            await add_category_handler(update, context)
        elif query.data == "delete_category":
            await delete_category_handler(update, context)

        elif query.data.startswith("deletecat_"):
            await confirm_delete_category(update, context)
        # ✅ Выбор категории → Показываем подкатегории
        elif query.data.startswith("category_"):
            context.user_data["prev_menu"].append("category_menu")  # Сохраняем текущий экран
            category_name = query.data.split("_")[1]
            context.user_data["selected_category"] = category_name

            subcategories = get_subcategories(context.user_data["operation_type"], context.user_data["selected_wallet"],
                                              category_name)

            await query.edit_message_text(
                text=f"🏷 Вы выбрали категорию: {category_name}.\nТеперь выберите подкатегорию:",
                reply_markup=InlineKeyboardMarkup([
                    *[[InlineKeyboardButton(subcat, callback_data=f"subcategory_{subcat}")] for subcat in
                      subcategories],
                    [InlineKeyboardButton("➕ Добавить подкатегорию", callback_data="add_subcategory")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back")]
                ])
            )

        elif query.data == "add_subcategory":
            await add_subcategory_handler(update, context)
        elif query.data == "delete_subcategory":
            await delete_subcategory_handler(update, context)

        elif query.data.startswith("deletesubcat_"):
            await confirm_delete_subcategory(update, context)
        # ✅ Выбор подкатегории → Показываем валюту
        elif query.data.startswith("subcategory_"):
            context.user_data["prev_menu"].append("subcategory_menu")  # Сохраняем текущий экран
            subcategory_name = query.data.split("_")[1]
            context.user_data["selected_subcategory"] = subcategory_name

            await show_currency_menu(update, context)

        elif query.data == "add_currency":
            await add_currency_handler(update, context)
        elif query.data == "delete_currency":
            await delete_currency_handler(update, context)

        elif query.data.startswith("deletecurrency_"):
            await confirm_delete_currency(update, context)

        # ✅ Выбор валюты → Вводим сумму
        elif query.data.startswith("currency_"):
            # Сохраняем предыдущее меню перед переходом
            context.user_data["prev_menu"].append("subcategory_menu")

            currency_name = query.data.split("_")[1]
            context.user_data["currency"] = currency_name

            await query.edit_message_text(
                text=f"Вы выбрали валюту: {currency_name}.\nТеперь введите сумму для транзакции:",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Пропустить", callback_data="skip_amount")],
                    [InlineKeyboardButton("🔙 Назад", callback_data="back_to_subcategory_menu")]
                ])
            )
            context.user_data["action"] = "add_amount"
        elif query.data == "back_to_subcategory_menu":
            await show_subcategories(update, context)  # ✅ Возвращает в подкатегории

            context.user_data["action"] = "add_amount"

        # ✅ Пропуск суммы → Вводим комментари
        elif query.data == "skip_amount":
            context.user_data["amount"] = "Пропущено"
            await query.edit_message_text(
                "Введите комментарий для операции или нажмите 'Пропустить':",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Пропустить", callback_data="skip_comment")]
                ])
            )
            context.user_data["action"] = "add_comment"

        # ✅ Пропуск комментария → Отправляем чек
        elif query.data == "skip_comment":
            context.user_data["comment"] = "Пропущено"
            await query.edit_message_text(
                "Отправьте фото чека или нажмите 'Пропустить':",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("Пропустить", callback_data="skip_receipt")]
                ])
            )
            context.user_data["action"] = "upload_receipt"
        elif query.data == "edit_amount":
            await edit_amount(update, context)


        # ✅ Пропуск чека → Сохраняем операцию и показываем результат
        elif query.data == "skip_receipt":
            context.user_data["receipt_id"] = "Пропущено"
            await save_operation(update,context)
            await query.edit_message_text(
                "✅ Операция завершена! Что дальше?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Начать новую операцию", callback_data="start")]
                ])
            )
        elif query.data == "dispaly_wallet_balance":
            await dispaly_wallet_balance(update, context)
            await update.message.reply_text(
                "✅ Операция завершена! Что дальше?",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Новая операция", callback_data="start")]
                ])
            )



        elif query.data == "back":

            if context.user_data["prev_menu"]:

                last_menu = context.user_data["prev_menu"].pop()  # Берем последнее меню

                if last_menu == "wallet_menu":

                    await show_wallet_menu(update, context)


                elif last_menu == "operation_menu":

                    await callback_handler(update, context)  # Показываем меню операций


                elif last_menu == "category_menu":

                    await show_categories(update, context)


                elif last_menu == "subcategory_menu":

                    await show_subcategories(update, context)


                elif last_menu == "currency_menu":

                    await show_currency_menu(update, context)


                else:

                    await show_wallet_menu(update, context)  # По умолчанию возвращаем в главное меню

            else:

                await show_wallet_menu(update, context)  # Если стек пуст, вернем в главное меню


        elif query.data == "start":

            await show_wallet_menu(update, context)  # Возвращаем в главное меню


        # ✅ Начать новую операцию → Перенаправляем в главное меню
        elif query.data == "start":
            await show_wallet_menu(update, context)  # ✅ Теперь возвращает корректное меню


    except Exception as e:
        logging.error(f"Ошибка в callback_handler: {e}")
        await context.bot.send_message(chat_id=query.from_user.id, text="❌ Произошла ошибка. Попробуйте снова.")

async def save_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Сохраняет операцию и обновляет баланс каждой валюты в кошельке отдельно.
    """
    try:
        wallet_name = context.user_data.get("selected_wallet")
        operation_type = context.user_data.get("operation_type")
        currency = context.user_data.get("currency")
        amount = context.user_data.get("amount")

        if not wallet_name or not currency or amount is None:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text="❌ Ошибка: данные операции не указаны."
            )
            return

        # 🔥 Загружаем данные
        data = load_data()
        wallet = data["wallets"].get(wallet_name, {})

        # ✅ Проверяем, что `currencies` - это **словарь**, а не список!
        if "currencies" not in wallet or not isinstance(wallet["currencies"], dict):
            wallet["currencies"] = {}  # Исправляем структуру, если там что-то не так

        # ✅ Проверяем, есть ли баланс для конкретной валюты
        if currency not in wallet["currencies"]:
            wallet["currencies"][currency] = 0  # Если валюты нет, создаем с 0

        current_balance = wallet["currencies"][currency]

        # 🔥 Обновляем баланс отдельно для каждой валюты
        if operation_type == "expense":
            if current_balance < amount:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id, text=f"❌ Недостаточно средств в {currency}! Баланс: {current_balance}"
                )
                return
            new_balance = current_balance - amount
        else:  # income
            new_balance = current_balance + amount

        # ✅ Обновляем баланс только для этой валюты
        wallet["currencies"][currency] = new_balance
        data["wallets"][wallet_name] = wallet
        save_data(data)  # ✅ Сохраняем изменения

        logging.info(f"✅ Баланс {currency} в кошельке '{wallet_name}' обновлен: {new_balance}")

        # ✅ Записываем в Google Sheets
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operations_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Операции")
        check_id = context.user_data.get("receipt_id", "Пропущено")
        category_name = context.user_data.get("selected_category", "Не указано")
        subcategory_name = context.user_data.get("selected_subcategory", "Не указано")
        comment = context.user_data.get("comment", "Пропущено")

        operations_sheet.append_row([
            date, operation_type, wallet_name, category_name, subcategory_name, currency, amount, comment, check_id
        ])

        logging.info("✅ Данные успешно записаны в Google Таблицу!")

        # ✅ Показываем обновленный баланс в Telegram
        await dispaly_wallet_balance(update, context)

        # 🔄 Очищаем контекст
        context.user_data.clear()

    except Exception as e:
        logging.error(f"❌ Ошибка в save_operation: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text="❌ Ошибка при сохранении операции. Попробуйте снова."
        )


async def save_operation_and_return_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        wallet_name = context.user_data.get("selected_wallet", "Не указано")
        operation_type = context.user_data.get("operation_type", "Не указано")
        category_name = context.user_data.get("selected_category", "Не указано")
        subcategory_name = context.user_data.get("selected_subcategory", "Не указано")
        currency = context.user_data.get("currency", "Не указано")
        amount = context.user_data.get("amount")
        comment = context.user_data.get("comment", "Пропущено")
        receipt_id = context.user_data.get("receipt_id", "Пропущено")  # ✅ Сохраняем ID чека
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logging.info(f"📊 Сохраняем операцию: {operation_type}, {wallet_name}, {currency}, {amount}, чек ID: {receipt_id}")

        if amount is None or not isinstance(amount, (int, float)) or amount <= 0:
            await update.message.reply_text("❌ Ошибка: сумма операции должна быть положительным числом.")
            return

        # 🔥 Загружаем и обновляем баланс
        data = load_data()
        wallet = data["wallets"].get(wallet_name, {})

        if "currencies" not in wallet:
            wallet["currencies"] = {}

        if currency not in wallet["currencies"]:
            wallet["currencies"][currency] = 0

        current_balance = wallet["currencies"][currency]

        if operation_type == "expense":
            new_balance = current_balance - amount
        else:
            new_balance = current_balance + amount

        wallet["currencies"][currency] = new_balance
        data["wallets"][wallet_name] = wallet
        save_data(data)

        logging.info(f"✅ Баланс {currency} обновлен: {new_balance}")

        # ✅ Записываем в Google Sheets
        operations_sheet = gc.open_by_key(SPREADSHEET_ID).worksheet("Операции")
        operations_sheet.append_row([
            date, operation_type, wallet_name, category_name, subcategory_name, currency, amount, comment, receipt_id
        ])

        logging.info(f"✅ Операция сохранена в Google Sheets с ID чека: {receipt_id}")

        # ✅ Обновляем баланс в Telegram
        await dispaly_wallet_balance(update, context)

        # 🔄 Очищаем контекст после сохранения
        context.user_data.clear()

    except Exception as e:
        logging.error(f"❌ Ошибка при сохранении данных: {e}")
        await update.message.reply_text("❌ Ошибка при сохранении данных. Попробуйте снова.")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обрабатывает отправку фото чека.
    """
    try:
        # Проверяем, есть ли фото в сообщении
        if not update.message or not update.message.photo:
            await update.message.reply_text("Ошибка: в сообщении отсутствует фото. Пожалуйста, отправьте фото чека.")
            return

        photo = update.message.photo[-1]  # Берем последнюю (самую качественную) версию фото
        file_id = photo.file_id  # ID файла фото в Telegram
        check_id = generate_check_id()  # Генерируем уникальный ID чека

        # Отправляем фото в группу с ID чека
        await context.bot.send_photo(
            chat_id=GROUP_CHAT_ID,
            photo=file_id,
            caption=f"Чек с ID: {check_id}"
        )

        # Сохраняем ID чека в контекст
        context.user_data["receipt_id"] = check_id

        # Вызываем метод для сохранения операции и возврата к старту
        await save_operation_and_return_to_start(update, context)

    except AttributeError as e:
        logging.error(f"Ошибка AttributeError в photo_handler: {e}")
        if update.message:
            await update.message.reply_text("Ошибка при обработке фото. Попробуйте снова.")
        else:
            logging.error("update.message отсутствует.")

    except Exception as e:
        logging.error(f"Ошибка в photo_handler: {e}")
        if update.message:
            await update.message.reply_text("Произошла ошибка при обработке фото чека. Пожалуйста, попробуйте снова.")
        else:
            logging.error("update.message отсутствует.")
async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновляет главное меню."""
    await start(update, context)
    await update.message.reply_text("🔄 Меню обновлено!")


async def report_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Перенаправляет в чат для сообщений об ошибках."""
    await update.message.reply_text(
        "🔗 Переходите в чат для сообщения об ошибке!",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("✉ Перейти в чат", url="https://t.me/mwnhn")]
        ])
    )

def main():


    """Запуск бота."""
    migrate_json_structure()



    application = Application.builder().token("7351753880:AAEVLbjdQp_etMQAIWp6flU-ZdjaQltVNAE").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt_photo))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_receipt_document))
    # Устанавливаем команды в меню Telegram
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("update", update_command))
    application.add_handler(CommandHandler("report", report_command))
    application.run_polling()


if __name__ == "__main__":
    main()
