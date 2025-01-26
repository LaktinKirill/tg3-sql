import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart


def create_db_connection():
    connection = sqlite3.connect('school_data.db')
    return connection, connection.cursor()


# Инициализация бота
API_TOKEN = '6972189764:AAE3ByZHHuIRx-RWn22HMC6QjQdg7rDkpfE'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Класс состояний
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    age INTEGER,
                    grade TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Обработчик команды /start
@dp.message(CommandStart())  # Изменен декоратор
async def start(message: types.Message, state: FSMContext):
    await message.reply("Привет! Давай зарегистрируем ученика. Введи имя:")
    await state.set_state(StudentForm.name)


# Обработчик отмены
@dp.message(Command("cancel"))  # Изменен декоратор
async def cancel_handler(message: types.Message, state: FSMContext):
    await state.clear()  # Используем clear() вместо finish()
    await message.reply("Ввод отменен")

# Обработчик имени
@dp.message(StudentForm.name)  # Убран параметр state=
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)  # Обновлен метод сохранения данных
    await message.reply("Отлично! Теперь введи возраст:")
    await state.set_state(StudentForm.age)
    
    
# Обработчик возраста
@dp.message(StudentForm.age)  # Убран параметр state=
async def process_age(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        if 1 <= age <= 120:
            await state.update_data(age=age)
            await state.set_state(StudentForm.grade)
            await message.reply("Хорошо! Теперь введи класс (например, 10-А):")
        else:
            await message.reply("Пожалуйста, введи корректный возраст (число от 1 до 120):")
    except ValueError:
        await message.reply("Возраст должен быть числом! Попробуй еще раз:")


# Обработчик класса
@dp.message(StudentForm.grade)
async def process_grade(message: types.Message, state: FSMContext):
    data = await state.get_data()
    data['grade'] = message.text
    
    # Создаем новое соединение для записи
    conn = sqlite3.connect('school_data.db')
    cursor = conn.cursor()
    try:
        # Сохраняем в базу данных
        cursor.execute('INSERT INTO students (name, age, grade) VALUES (?, ?, ?)',
                      (data['name'], data['age'], data['grade']))
        conn.commit()
        await state.clear()
        await message.reply("Данные успешно сохранены! Для нового ввода нажми /start")
    except sqlite3.Error as e:
        await message.reply(f"Произошла ошибка при сохранении: {e}")
    finally:
        conn.close()



async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())