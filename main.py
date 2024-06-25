import random
import pandas as pd
from datetime import datetime, timedelta
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import create_engine, Column, String, Integer, LargeBinary, BigInteger, DateTime, func, TIMESTAMP
from sqlalchemy.exc import DataError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.functions import now

from button import main_rp, order_keyboard, food_delete, order_keyboart

API_TOKEN = "6801433229:AAGxu_bosviMySCVgrBDO5urzlHtT_azsco"
from aiogram.dispatcher.filters.state import StatesGroup, State

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

storage = MemoryStorage()
dp.storage = storage
# DATABASE_URL = "postgresql://postgres:1@localhost:5432/admin"
DATABASE_URL = "sqlite:///hisobot.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Zayafka(Base):
    __tablename__ = 'zayafka'

    id = Column(Integer, primary_key=True)
    image = Column(LargeBinary)
    name = Column(String)


class Users(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger)
    username = Column(String, default=None)


class Hisobot(Base):
    __tablename__ = 'hisobot'
    id = Column(Integer, primary_key=True)
    zayafka = Column(String, default=None)
    fullname = Column(String, default=None)
    address = Column(String, default=None)
    fikr = Column(String, default=None)
    created_at = Column(TIMESTAMP, server_default=func.now())


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session()


class Form(StatesGroup):
    image = State()
    name = State()


class Delete(StatesGroup):
    name = State()


class Forms(StatesGroup):
    fullname = State()
    address = State()
    fikr = State()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@dp.message_handler(commands=['start', 'Back'])
async def start_order(message: types.Message):
    if message.from_user.id == 5772722670:
        await message.answer("Salom admin", reply_markup=main_rp)
    else:

        user_id = message.from_user.id
        username = message.from_user.username

        try:
            existing_user = session.query(Users).filter_by(user_id=user_id).first()
            if not existing_user:
                user = Users(user_id=user_id, username=username)
                session.add(user)
                session.commit()
                await message.answer("Привет! Добро пожаловать и бот-помощник информационных технологий!")
            else:
                await message.answer("Привет! Добро пожаловать и бот-помощник информационных технологий!")
        except DataError as e:
            session.rollback()
            print(f"DataError: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        except Exception as e:
            session.rollback()
            print(f"Unexpected error: {e}")
            await message.answer("Произошла ошибка. Пожалуйста, попробуйте еще раз.")
        await fetch_and_send_info(message)


@dp.message_handler(lambda message: message.text == "Zayafka qo'shish")
async def start_food_registration(message: types.Message):
    await message.answer("Iltimos,rasim kiriting")
    await Form.image.set()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Form.image)
async def process_food_picture(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    async with state.proxy() as data:
        data['image'] = photo_id

    await Form.next()
    await message.answer("Zayafka nomini kiriting:")


@dp.message_handler(state=Form.name)
async def process_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text

        file_id = data['image']
        file = await bot.get_file(file_id)
        downloaded_file = await bot.download_file(file.file_path)

        db = Session()
        food = Zayafka(
            image=downloaded_file.read(),
            name=data['name'],
        )
        db.add(food)
        db.commit()

        await state.finish()
        await message.answer(
            f"Zayafka nomi '{data['name']}"
        )


async def fetch_and_send_info(message: types.Message):
    db = Session()
    food_items = db.query(Zayafka).all()
    db.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for food_item in food_items:
        button_text = f"{food_item.name}"
        keyboard.add(types.KeyboardButton(text=button_text))

    await bot.send_message(chat_id=message.chat.id, text='заявку', reply_markup=keyboard)


async def hamma_ovqatlar(message: types.Message):
    db = Session()
    food_items = db.query(Zayafka).all()
    db.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for food_item in food_items:
        button_text = f"{food_item.food_name}"
        keyboard.add(types.KeyboardButton(text=button_text))

    keyboard.add(types.KeyboardButton(text="Back"))

    await bot.send_message(chat_id=message.chat.id, text="Mavjud Zayafkalar:", reply_markup=keyboard)


@dp.message_handler(
    lambda message: any(food_item.name in message.text for food_item in Session().query(Zayafka).all()))
async def show_food_details(message: types.Message):
    db = Session()
    selected_food_name = next(
        (food_item.name for food_item in db.query(Zayafka).all() if food_item.name in message.text), None)
    if message.from_user.id != 1327286056:
        if selected_food_name:
            try:

                selected_food_item = db.query(Zayafka).filter(Zayafka.name == selected_food_name).first()

                photo = selected_food_item.image
                details_text = f"{selected_food_item.name}\n"
                await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=details_text,
                                     reply_markup=order_keyboard(), )
            finally:
                db.close()
    else:
        if selected_food_name:
            try:

                selected_food_item = db.query(Zayafka).filter(Zayafka.name == selected_food_name).first()

                photo = selected_food_item.image
                details_text = f" Zayafka raqami : {selected_food_item.id}\nZayafka nomi: {selected_food_item.name}\n"
                await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=details_text,
                                     reply_markup=food_delete())
            finally:
                db.close()


@dp.message_handler(lambda message: message.text == "Zayafka ko'rish")
async def start_food_registration(message: types.Message):
    await food_info(message)


async def food_info(message: types.Message):
    db = Session()
    food_items = db.query(Zayafka).all()
    db.close()

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for food_item in food_items:
        button_text = f"{food_item.name}"
        keyboard.add(types.KeyboardButton(text=button_text))

    delete_button = types.KeyboardButton(text="🔙Orqaga")
    keyboard.add(delete_button)
    await bot.send_message(chat_id=message.chat.id, text="Mavjud Zayafkalar:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "🔙Orqaga")
async def start_food_registration(message: types.Message):
    await message.answer('Salom admin :', reply_markup=main_rp)


def get_selected_food_name():
    session = Session()
    food_items = session.query(Zayafka).all()

    if food_items:
        available_food_names = [food_item.name for food_item in food_items]
        selected_food_name = random.choice(available_food_names)
        return selected_food_name
    else:
        return None


def delete_selected_food_name():
    session = Session()
    food_items = session.query(Zayafka).all()

    if food_items:
        available_food_names = [food_item.name for food_item in food_items]
        selected_food_name = random.choice(available_food_names)
        return selected_food_name
    else:
        return None


@dp.callback_query_handler(lambda query: query.data == 'order_start', state="*")
async def process_order(query: types.CallbackQuery, state: FSMContext):
    await query.answer()

    selected_food_name = get_selected_food_name()

    async with state.proxy() as data:
        data['name'] = selected_food_name

    await Forms.fullname.set()
    await query.message.answer("Пожалуйста введите свое полное имя:")


@dp.message_handler(state=Forms.fullname)
async def process_fullname(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fullname'] = message.text
    await Forms.next()
    await message.answer("Введите кафедру или лабораторию и номер кабинета.")


@dp.message_handler(state=Forms.address)
async def process_phone_number(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await Forms.next()
    await message.answer("Добавьте дополнительные мысли и комментарии.")


@dp.message_handler(state=Forms.fikr)
async def process_address(message: types.Message, state: FSMContext):
    session = Session()
    async with state.proxy() as data:
        data['fikr'] = message.text

        order_info = (
            f"Zayafka nomi: {data['name']}\n"
            f"Buyurtmachining ismi: {data['fullname']}\n"
            f"Buyurtmachinning bo'lim,labaratoriya va xona raqami: {data['address']}\n"
            f"Buyurtmachining qo'shimcha fikr va mulohazasi: {data['fikr']}\n"
        )
        db = Session()
        hisobot = Hisobot(
            zayafka=data['name'],
            fullname=data['fullname'],
            address=data['address'],
            fikr=data['fikr']
        )
        db.add(hisobot)
        db.commit()

        # admin_id = '1327286056'
        admins = '5772722670'
        # await bot.send_message(admin_id, f"New order:\n\n{order_info}", reply_markup=order_keyboart())
        await bot.send_message(admins, f"New order:\n\n{order_info}", reply_markup=order_keyboart())
        await message.answer(
            "Ваш запрос отправлен администратору, наш администратор свяжется с вами в ближайшее время! Спасибо")
        await state.finish()


@dp.callback_query_handler(lambda query: query.data.startswith("o'chirish"))
async def delete_message(query: types.CallbackQuery):
    chat_id = query.message.chat.id
    await bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    await bot.send_message(chat_id=chat_id, text=f' Buyurtma o''chirildi')


async def send_info_to_users():
    db = Session()
    users = db.query(Users).all()

    for user in users:
        try:
            await bot.send_message(user.user_id, "🛠 Web site and telegram bot creation service\n"
                                                 "️ ️ We offer you the service of creating a website and telegram bots at reasonable prices\n"
                                                 "👨🏻‍💻 Occupation: Python Developer\n"
                                                 "💰 Salary: Negotiable\n"
                                                 "💬 Contact: @mirpolatov_m\n"
                                                 "📞 Phone: +998946032306")
        except Exception as e:
            print(f"Error sending message to user {user.user_id}: {e}")

    db.close()


# async def on_startup(dp):
#     scheduler = AsyncIOScheduler()
#     scheduler.add_job(send_info_to_users, 'interval', seconds=10000)
#     scheduler.start()

ADMIN_ID = 5772722670


# @dp.message_handler(commands=['send_report'])
# async def send_report(message: types.Message):
#         # Query the database
#         hisobot_data = session.query(Hisobot).all()
#
#         # Prepare data for the DataFrame
#         data = [
#             {
#                 'ID': record.id,
#                 'Zayafka': record.zayafka,
#                 'Fullname': record.fullname,
#                 'Address': record.address,
#                 'Fikr': record.fikr,
#
#             }
#             for record in hisobot_data
#         ]
#
#         # Create a DataFrame
#         df = pd.DataFrame(data)
#
#         # Save to Excel
#         file_path = 'hisobot_report.xlsx'
#         df.to_excel(file_path, index=False)
#
#         # Send the file to the admin
#         await bot.send_document(chat_id=ADMIN_ID, document=open(file_path, 'rb'))
#
#         # Clean up
#         os.remove(file_path)
# else:
#     await message.reply("You are not authorized to use this command.")

@dp.message_handler(commands=['1_oy_hisobot'])
async def send_report(message: types.Message):
    one_month_ago = datetime.now() - timedelta(days=30)

    hisobot_data = session.query(Hisobot).filter(Hisobot.created_at >= one_month_ago).all()

    if not hisobot_data:
        await bot.send_message(chat_id=ADMIN_ID, text="Bu oyda zayafka mavjud emas.")
    else:
        data = [
            {
                'ID': record.id,
                'Zayafka': record.zayafka,
                'Fullname': record.fullname,
                'Address': record.address,
                'Fikr': record.fikr,
                'Vaqti': record.created_at
            }
            for record in hisobot_data
        ]

        df = pd.DataFrame(data)

        file_path = '1-oylik_hisobot.xlsx'
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width


            worksheet.column_dimensions['F'].width = 20

        await bot.send_document(chat_id=ADMIN_ID, document=open(file_path, 'rb'))

        os.remove(file_path)

@dp.message_handler(commands=['3_oy_hisobot'])
async def send_report(message: types.Message):
    one_month_ago = datetime.now() - timedelta(days=90)

    hisobot_data = session.query(Hisobot).filter(Hisobot.created_at >= one_month_ago).all()

    if not hisobot_data:
        await bot.send_message(chat_id=ADMIN_ID, text="Bu oyda zayafka mavjud emas.")
    else:
        data = [
            {
                'ID': record.id,
                'Zayafka': record.zayafka,
                'Fullname': record.fullname,
                'Address': record.address,
                'Fikr': record.fikr,
                'Vaqti': record.created_at
            }
            for record in hisobot_data
        ]

        df = pd.DataFrame(data)

        file_path = '3-oylik_hisobot.xlsx'
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width


            worksheet.column_dimensions['F'].width = 20

        await bot.send_document(chat_id=ADMIN_ID, document=open(file_path, 'rb'))

        os.remove(file_path)

@dp.message_handler(commands=['6_oy_hisobot'])
async def send_report(message: types.Message):
    one_month_ago = datetime.now() - timedelta(days=180)

    hisobot_data = session.query(Hisobot).filter(Hisobot.created_at >= one_month_ago).all()

    if not hisobot_data:
        await bot.send_message(chat_id=ADMIN_ID, text="Bu oyda zayafka mavjud emas.")
    else:
        data = [
            {
                'ID': record.id,
                'Zayafka': record.zayafka,
                'Fullname': record.fullname,
                'Address': record.address,
                'Fikr': record.fikr,
                'Vaqti': record.created_at
            }
            for record in hisobot_data
        ]

        df = pd.DataFrame(data)

        file_path = '6-oy_hisobot.xlsx'
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width


            worksheet.column_dimensions['F'].width = 20

        await bot.send_document(chat_id=ADMIN_ID, document=open(file_path, 'rb'))

        os.remove(file_path)

@dp.message_handler(commands=['1_yillik_hisobot'])
async def send_report(message: types.Message):
    one_month_ago = datetime.now() - timedelta(days=365)

    hisobot_data = session.query(Hisobot).filter(Hisobot.created_at >= one_month_ago).all()

    if not hisobot_data:
        await bot.send_message(chat_id=ADMIN_ID, text="Bu oyda zayafka mavjud emas.")
    else:
        data = [
            {
                'ID': record.id,
                'Zayafka': record.zayafka,
                'Fullname': record.fullname,
                'Address': record.address,
                'Fikr': record.fikr,
                'Vaqti': record.created_at
            }
            for record in hisobot_data
        ]

        df = pd.DataFrame(data)

        file_path = '1-yillik_hisobot.xlsx'
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            worksheet = writer.sheets['Sheet1']
            for col in worksheet.columns:
                max_length = 0
                column = col[0].column_letter
                for cell in col:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2)
                worksheet.column_dimensions[column].width = adjusted_width


            worksheet.column_dimensions['F'].width = 20

        await bot.send_document(chat_id=ADMIN_ID, document=open(file_path, 'rb'))

        os.remove(file_path)

@dp.callback_query_handler(lambda query: query.data == 'delete', state="*")
async def process_delete(query: types.CallbackQuery, state: FSMContext):
    await query.answer()
    selected_food_name = delete_selected_food_name()

    async with state.proxy() as data:
        data['name'] = selected_food_name

        if selected_food_name:
            db = Session()
            food_item = db.query(Zayafka).filter_by(name=selected_food_name).first()

            if food_item:
                db.delete(food_item)
                db.commit()
                db.close()
                chat_id = query.message.chat.id

                await bot.send_message(chat_id=chat_id, text='✅ Malumotlarni o\'chirildi')

                data.clear()
                message_id = query.message.message_id

                await bot.delete_message(chat_id=chat_id, message_id=message_id)
        else:
            await bot.answer_callback_query(query.id, text='❌ Ma\'lumot topilmadi')


if __name__ == '__main__':
    from aiogram import executor
    from aiogram import types

    executor.start_polling(dp, skip_updates=True, loop=dp.loop)
