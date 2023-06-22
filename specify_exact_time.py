import logging

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime ,timedelta
from fpdf import FPDF
import unicodedata
import os
import psycopg2


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN='YOUR-TOKEN'

conn = psycopg2.connect(
    host="localhost",
    database="bot",
    user="botuser",
    password="password1721"
)

cursor = conn.cursor()

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def create_attendance_table():
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS my_table (
        id SERIAL PRIMARY KEY,
        user_id BIGINT,
        name VARCHAR(255),
        date DATE,
        came_time TIME,
        left_time TIME
    );
    '''
    cursor.execute(create_table_query)
    conn.commit()

create_attendance_table()


class UnicodePDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Davomod hissoboti', align='C', ln=1)

       
        

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Copyright 2023 - Quantic-Co', align='C')



def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Attendance Bot!")


# Register the start command handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def help(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
                                *Bu bot foydalanuvchilarga botga “+” yoki “-” xabarini yuborish orqali o‘z ishtirokini belgilash imkonini beradi.Agar kelgan va ketgan vaqtingizni yozmoqchi bo'lsangiz , '+' va '-' dan keyin bir bo'sh joy qoldirib vaqtni kiriting.          Masalan: '+ 9:00'*""",
                                parse_mode=ParseMode.MARKDOWN)


help_handler = CommandHandler('info', help)
dispatcher.add_handler(help_handler)



# Dictionary to store attendance information
attendance_data = {}




def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if message_text.startswith('+') or message_text.startswith('-'):
        parts = message_text.split(' ')
        if len(parts) > 1:
            time_value = parts[1]
            if time_value.count(':') == 1:
                current_time = time_value

    if message_text.startswith('+'):
        if user.id not in attendance_data:
            attendance_data[user.id] = {'name': user.first_name, 'dates': {current_date: {'came': [current_time]}}}
        elif current_date not in attendance_data[user.id]['dates']:
            attendance_data[user.id]['dates'][current_date] = {'came': [current_time]}
        else:
            attendance_data[user.id]['dates'][current_date]['came'].append(current_time)

    elif message_text.startswith('-'):
        if user.id in attendance_data and current_date in attendance_data[user.id]['dates']:
            if 'left' in attendance_data[user.id]['dates'][current_date]:
                attendance_data[user.id]['dates'][current_date]['left'].append(current_time)
            else:
                attendance_data[user.id]['dates'][current_date]['left'] = [current_time]


message_handler = MessageHandler(
    Filters.text & ~Filters.command, collect_attendance)
dispatcher.add_handler(message_handler)

def generate_attendance_table(update: Update, context):
    pdf = UnicodePDF()
    pdf.add_page()
    font_path = '/home/behzod/django/fullbot/dejavu-sans-ttf-2.37 (1)/dejavu-sans-ttf-2.37/DejaVuSans.ttf'
    pdf.add_font('DejaVuSans', '', font_path, uni=True)
    pdf.set_font('DejaVuSans', '', 12)

    pdf.cell(15, 15, 'ID')
    pdf.cell(30, 15, 'User')
    pdf.cell(40, 15, 'Date')
    pdf.cell(50, 15, 'Came')
    pdf.cell(50, 15, 'Left')
    pdf.ln()

    id_counter = 1
    for user_id, data in attendance_data.items():
        user_name = data.get('name', '')
        dates = data.get('dates', {})

        for date, entry_data in dates.items():
            came_times = entry_data.get('came', [])
            left_times = entry_data.get('left', [])

            user_name = str(user_name)
            date = str(date)

            max_rows = max(len(came_times), len(left_times))

            for row in range(max_rows):
                pdf.cell(15, 15, str(id_counter))
                pdf.cell(30, 15, user_name if row == 0 else '')  # Display user name only in the first row
                pdf.cell(40, 15, date if row == 0 else '')  # Display date only in the first row

                # Display the arrival time in the current row
                if row < len(came_times):
                    pdf.cell(50, 15, came_times[row])
                else:
                    pdf.cell(50, 15, '')  # Leave the cell empty if there are no more arrival times

                # Display the departure time in the current row
                if row < len(left_times):
                    pdf.cell(50, 15, left_times[row])
                else:
                    pdf.cell(50, 15, '')  # Leave the cell empty if there are no more departure times

                pdf.ln()
                id_counter += 1

    pdf_file = 'Attendance.pdf'
    pdf.output(pdf_file)

    with open(pdf_file, 'rb') as file:
        context.bot.send_document(
            chat_id=update.effective_chat.id, document=file, caption='Davomod hisoboti')


def show_menu(update: Update, context):
    menu_options = [
        ['/start', '/menu'],  # List of available commands/options
        ['/info'],  # to give information
        ['+', '-' ],  # came and left work
        ['/hisob'],  # Generate attendance table
        ['/lastweek'],  # it sends last week's attendance
        ['/lastmonth'],  # it sends last month's attendance
    ]
    reply_markup = ReplyKeyboardMarkup(menu_options, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Selected option:", reply_markup=reply_markup)
def menu(update: Update, context):
    show_menu(update, context)
    
menu = CommandHandler('menu' , show_menu)
dispatcher.add_handler(menu)

hisob_handler = CommandHandler('hisob', generate_attendance_table)
dispatcher.add_handler(hisob_handler)

updater.start_polling()
updater.idle()
