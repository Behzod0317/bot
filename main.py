import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime
from fpdf import FPDF
import unicodedata
import os
import psycopg2
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

TOKEN = '6082028232:AAG0tngUrjsf7HvPO_HOFddVr2Uiw2o5J8s'


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
    CREATE TABLE IF NOT EXISTS attendance (
        id SERIAL PRIMARY KEY,
        user_id INTEGER,
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
       
        pass

    def footer(self):
        
        pass


def start(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Welcome to the Attendance Bot!")


# Register the start command handler
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)


def help(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""
                                Bu bot foydalanuvchilarga botga “+” yoki “-” 
                                xabarini yuborish orqali o‘z ishtirokini
                                belgilash imkonini beradi. Bot ishtirokchilar 
                                haqidagi ma'lumotlarni, jumladan,
                                foydalanuvchining ismi, sanasi va kelish yoki
                                ketish vaqtini pdf formatda qaytaradi.""")


help_handler = CommandHandler('help', help)
dispatcher.add_handler(help_handler)
# Dictionary to store attendance information
attendance_data = {}


# def collect_attendance(update: Update, context):
#     message_text = update.message.text.strip()
#     user = update.message.from_user
#     now = datetime.now()
#     current_time = now.strftime("%H:%M:%S")
#     current_date = now.strftime("%Y-%m-%d")

#     if message_text == '+':
#         if user.id not in attendance_data:
#             attendance_data[user.id] = {
#                 'name': user.first_name, 'coming_time': current_time}
#     elif message_text == '-':
#         if user.id in attendance_data:
#             attendance_data[user.id]['leaving_time'] = current_time



def collect_attendance(update: Update, context):
    message_text = update.message.text.strip()
    user = update.message.from_user
    now = datetime.now()
    current_time = now.strftime("%H:%M")
    current_date = now.strftime("%Y-%m-%d")

    if message_text == '+':
        if user.id not in attendance_data:
            attendance_data[user.id] = {'name': user.first_name, 'dates': {current_date: {'came': [current_time]}}}
        elif current_date not in attendance_data[user.id]['dates']:
            attendance_data[user.id]['dates'][current_date] = {'came': [current_time]}
        else:
            attendance_data[user.id]['dates'][current_date]['came'].append(current_time)

            
    elif message_text == '-':
        if user.id in attendance_data and current_date in attendance_data[user.id]['dates']:
            if 'left' in attendance_data[user.id]['dates'][current_date]:
                attendance_data[user.id]['dates'][current_date]['left'].append(current_time)
            else:
                attendance_data[user.id]['dates'][current_date]['left'] = [current_time]

message_handler = MessageHandler(
    Filters.text & ~Filters.command, collect_attendance)
dispatcher.add_handler(message_handler)

# def generate_attendance_table(update: Update, context):
#     pdf = UnicodePDF()
#     pdf.add_page()
#     font_path = os.path.join(os.path.dirname(__file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
#     pdf.add_font('DejaVuSans', '', font_path, uni=True)
#     pdf.set_font('DejaVuSans', '', 12)

#     pdf.cell(15, 15, 'ID')
#     pdf.cell(30, 15, 'User')
#     pdf.cell(40, 15, 'Date')
#     pdf.cell(50, 15, 'Came')
#     pdf.cell(50, 15, 'Left')
#     pdf.ln()

#     id_counter = 1
#     for user_id, data in attendance_data.items():
#         user_name = data.get('name', '')
#         dates = data.get('dates', {})

#         for date, entry_data in dates.items():

#             came_times = []  # Initialize came_times as an empty list
#             left_times = []  
#             # came_times = entry_data.get('came', [])
#             # left_times = entry_data.get('left', [])
#             # came_times.append(entry['came'][:5])  # Remove the seconds part from each time
#             # left_times.append(entry['left'][:5]) 
#             for entry in entry_data:
#                 if isinstance(entry, dict):
#                     came_time = entry.get('came')
#                     left_time = entry.get('left')

#                     # Remove the seconds part from each time
#                     came_time = came_time[:5] if came_time else ''
#                     left_time = left_time[:5] if left_time else ''

#                     came_times.append(came_time)
#                     left_times.append(left_time)

#             # Join the came_times and left_times into a single string
#             came_times_str = ', '.join(came_times)
#             left_times_str = ', '.join(left_times)


#             user_name = str(user_name)
#             date = str(date)

#             pdf.cell(15, 15, str(id_counter))
#             pdf.cell(30, 15, user_name or '')
#             pdf.cell(40, 15, date)
#             pdf.cell(50, 15, ', '.join(came_times))
#             pdf.cell(50, 15, ', '.join(left_times) if left_times else '')
#             pdf.ln()
#             id_counter += 1

#     pdf_file = 'Attendance.pdf'
#     pdf.output(pdf_file)

#     with open(pdf_file, 'rb') as file:
#         context.bot.send_document(
#             chat_id=update.effective_chat.id, document=file, caption='Davomod hisoboti')
def generate_attendance_table(update: Update, context):
    pdf = UnicodePDF()
    pdf.add_page()
    font_path = os.path.join(os.path.dirname(__file__), 'dejavu-sans-ttf-2.37', 'DejaVuSans.ttf')
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

        #     pdf.cell(15, 15, str(id_counter))
        #     pdf.cell(30, 15, user_name or '')
        #     pdf.cell(40, 15, date)
        #     pdf.cell(50, 15, ', '.join(came_times))
        #     pdf.cell(50, 15, ', '.join(left_times) if left_times else '')
        #     pdf.ln()
        #     id_counter += 1
            # max_len = max(len(came_times), len(left_times))

            # for i in range(max_len):
            #     pdf.cell(15, 15, str(id_counter))
            #     pdf.cell(30, 15, user_name or '')
            #     pdf.cell(40, 15, date)
            #     pdf.cell(50, 15, came_times[i] if i < len(came_times) else '')
            #     pdf.cell(50, 15, left_times[i] if i < len(left_times) else '')
            #     pdf.ln()
            #     id_counter += 1
       

    # Calculate the maximum number of rows required for this entry
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

hisob_handler = CommandHandler('hisob', generate_attendance_table)
dispatcher.add_handler(hisob_handler)


def show_menu(update: Update, context):
    menu_options = [
        ['/start', '/menu'],  # List of available commands/options
        ['/help'],  # to give information
        ['+'],  # Attend
        ['-'],  # Leave
        ['/hisob'],  # Generate attendance table
    ]
    reply_markup = ReplyKeyboardMarkup(menu_options, resize_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Selected option:", reply_markup=reply_markup)


# Register the menu command handler
menu_handler = CommandHandler('menu', show_menu)
dispatcher.add_handler(menu_handler)
updater.start_polling()
updater.idle()
