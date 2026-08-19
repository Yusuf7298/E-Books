from typing import Final, Dict, List, Optional
# pyrefly: ignore [missing-import]
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# pyrefly: ignore [missing-import]
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from enum import Enum
from pathlib import Path
import re
import logging
import sys
import os
from dotenv import load_dotenv
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

TOKEN: Final = os.environ.get("BOT_TOKEN", "")
if not TOKEN:
    raise RuntimeError(
        "Missing BOT_TOKEN. Set it in .env or export it in your shell environment."
    )

BOT_USERNAME: Final = "@EthioEducationalsBot"
PRIVATE_CHANNEL_ID: Final = "-1002976173648"
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotState(Enum):
    """Enums for bot states, replacing string constants."""
    MAIN = "main"
    STUDENT_GRADE = "student_grade"
    TEACHER_GRADE = "teacher_grade"
    TRACK_SELECTION = "track_selection"

USER_STATE_KEY: Final = "STATE"
PENDING_GRADE_KEY: Final = "PENDING_GRADE"
PENDING_STATE_KEY: Final = "PENDING_STATE"
MESSAGE_HISTORY_KEY: Final = "MSG_HISTORY" 
STUDENT_DIR: Final = "Students_Books"
TEACHER_DIR: Final = "Teachers_Guide"
NATURAL_SCIENCE: Final = "Natural Science"
SOCIAL_SCIENCE: Final = "Social Science"
AVAILABLE_GRADES: Final[List[str]] = ['9', '10', '11', '12']
TRACK_GRADES: Final[List[str]] = ['11', '12']


CONTACT_INFO: Final[str] = (
    "🌐 Contact & Recommended Bots\n\n"
    "🎓 Study Bot: Practice & study with [📚 Ethio-Smart Study](https://t.me/EthioSmartStudy_bot)\n\n"
    "Telegram: [Ño 🕕 4 ... ](https://t.me/Cs1At07)\n"
    "Instagram: [Yusuf Mohammed](https://www.instagram.com/kebilad_7488/)\n" 
    "Email: [ym47484988@gmail.com](mailto:ym47484988@gmail.com)\n"
    "LinkedIn: [Yusuf Mohammed](https://www.linkedin.com/in/yusuf-mohammed-5272572b6/)\n\n"
    "For more follow me on\n\n"
    "Telegram Channel: [Yusuf Moh](https://t.me/yusufcodes)\n"
    "Instagram: [Yusuf Mohammed](https://www.instagram.com/kebilad_7488/)\n\n"
    "Feel free to reach out for any assistance or inquiries!"
)
NAVIGATION_ROW = [
    KeyboardButton("Back ↩️"),
    KeyboardButton("Main Menu 🏠"),
    KeyboardButton("Clear Menu ❌")
]
MAIN_MENU_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton("📚 Get Student Books")],
        [KeyboardButton("👨‍🏫 Get Teacher Guides")],
        [KeyboardButton("📞 Let's Contact")],
        NAVIGATION_ROW[1:3]
    ],
    resize_keyboard=True, one_time_keyboard=False
)
def create_grade_keyboard(grades_list: List[str]) -> ReplyKeyboardMarkup:
    grades = sorted(grades_list, key=int)
    keyboard_layout = []
    current_row = []
    for i, grade in enumerate(grades):
        current_row.append(KeyboardButton(f"Grade {grade}"))
        if (i + 1) % 2 == 0:
            keyboard_layout.append(current_row)
            current_row = []
    if current_row:
        keyboard_layout.append(current_row)
    keyboard_layout.append(NAVIGATION_ROW)
    return ReplyKeyboardMarkup(keyboard_layout, resize_keyboard=True, one_time_keyboard=False)

STUDENT_GRADE_KEYBOARD = create_grade_keyboard(AVAILABLE_GRADES)
TEACHER_GRADE_KEYBOARD = create_grade_keyboard(AVAILABLE_GRADES)
TRACK_KEYBOARD = ReplyKeyboardMarkup(
    [
        [KeyboardButton(f"{NATURAL_SCIENCE} 🧪"), KeyboardButton(f"{SOCIAL_SCIENCE} 📜")],
        NAVIGATION_ROW
    ],
    resize_keyboard=True, one_time_keyboard=False
)

class BookMetadata:
    def __init__(self, name: str, source_chat_id: str, message_id: int):
        self.name = name
        self.source_chat_id = source_chat_id 
        self.message_id = message_id 

BOOK_DATA: Dict[str, Dict[str, Dict[str, List[BookMetadata]]]] = {
    '9': {
        STUDENT_DIR: {
            '': [
                BookMetadata("Biology Grade 9 Student TextBook", PRIVATE_CHANNEL_ID, 3), 
                BookMetadata("Maths Grade 9 Student Book", PRIVATE_CHANNEL_ID, 4),
                BookMetadata(" Kitaaba Barataa Afan Oromo Kutaa 9", PRIVATE_CHANNEL_ID, 5),
                BookMetadata("Geography Grade 9 Student TextBook", PRIVATE_CHANNEL_ID, 6),
                BookMetadata("It Students Textbook Final June 23 2022 Compressed", PRIVATE_CHANNEL_ID, 7),
                BookMetadata("Chemistry Grade 9 Student Book", PRIVATE_CHANNEL_ID, 8),
                BookMetadata("HPE Grade 9 Student Book", PRIVATE_CHANNEL_ID, 9),
                BookMetadata("Economics Grade 9 Student Book", PRIVATE_CHANNEL_ID, 10),
                BookMetadata("Citizenship Grade 9 Student Book", PRIVATE_CHANNEL_ID, 11),
                BookMetadata("History Grade 9 Student Book", PRIVATE_CHANNEL_ID, 13),
                BookMetadata("English Grade 9 Student Book", PRIVATE_CHANNEL_ID, 17),
                BookMetadata("Physics Grade 9 Student Book", PRIVATE_CHANNEL_ID, 12),
                BookMetadata("PVA Grade 9 Student Book", PRIVATE_CHANNEL_ID, 29),
                BookMetadata("Amharic Grade 9 Student Book", PRIVATE_CHANNEL_ID, 46),
            ]
        },
        TEACHER_DIR: {
            '': [
                BookMetadata("Economics Grade 9 Teacher Guide S Tg", PRIVATE_CHANNEL_ID, 19), 
                BookMetadata("Maths Grade 9 Teacher Guide 2Aug22", PRIVATE_CHANNEL_ID, 20),
                BookMetadata("It Grade 9 Teacher'S Guide", PRIVATE_CHANNEL_ID, 21),
                BookMetadata("Physics Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 22),
                BookMetadata("English Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 23),
                BookMetadata("History Grade 9 Teachers Guide", PRIVATE_CHANNEL_ID, 24),
                BookMetadata("Geography Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 25),
                BookMetadata("Biology Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 26),
                BookMetadata("Hpe Grade 9 Teacher Guide Final", PRIVATE_CHANNEL_ID, 27),
                BookMetadata("Chemistry Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 28),
                BookMetadata("PVA Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 30),
                BookMetadata("Citizenship Grade 9 Teacher Guide", PRIVATE_CHANNEL_ID, 31),
            ]
        }
    },
    '10': {
        STUDENT_DIR: {
            '': [
                BookMetadata("HPE Grade 10 Students Books", PRIVATE_CHANNEL_ID, 33), 
                BookMetadata("History Grade 10 Students Books", PRIVATE_CHANNEL_ID, 34),
                BookMetadata("Geography Grade 10 Students Books", PRIVATE_CHANNEL_ID, 35), 
                BookMetadata("English Grade 10 Students Books", PRIVATE_CHANNEL_ID, 36),
                BookMetadata("Economics Grade 10 Students Books", PRIVATE_CHANNEL_ID, 37), 
                BookMetadata("Citizenship Grade 10 Students Books", PRIVATE_CHANNEL_ID, 38),
                BookMetadata("Chemistry Grade 10 Students Books", PRIVATE_CHANNEL_ID, 39), 
                BookMetadata("Biology Grade 10 Students Books", PRIVATE_CHANNEL_ID, 40),
                BookMetadata("Amharic Grade 10 Students Books", PRIVATE_CHANNEL_ID, 41),
                BookMetadata("Mathematics Grade 10 Students Books", PRIVATE_CHANNEL_ID, 42), 
                BookMetadata("Physics Grade 10 Students Books", PRIVATE_CHANNEL_ID, 43),
                BookMetadata("IT Grade 10 Students Books", PRIVATE_CHANNEL_ID, 44), 
                BookMetadata("Afan Oromo Grade 10 Students Books", PRIVATE_CHANNEL_ID, 45),
            ]
        },
        TEACHER_DIR: {
            '': [
                BookMetadata("Citizenship Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 48),
                BookMetadata("History Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 49),
                BookMetadata("Physics Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 50),
                BookMetadata("HPE Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 51),
                BookMetadata("Maths Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 52),
                BookMetadata("Geography Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 53),
                BookMetadata("Biology Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 54),
                BookMetadata("Afan Oromo Grade 10 Teachers Guide", PRIVATE_CHANNEL_ID, 55),
            ]
        }
    },
    
    '11': {
        STUDENT_DIR: {
            NATURAL_SCIENCE: [
                BookMetadata("Agriculture Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 57), 
                BookMetadata("Biology Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 58),
                BookMetadata("Chemistry Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 59),
                BookMetadata("English Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 60),
                BookMetadata("IT Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 61),
                BookMetadata("Mathematics Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 62),
                BookMetadata("Physics Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 63),
                BookMetadata("Kitaaba Barataa Afan Oromo Kutaa 11", PRIVATE_CHANNEL_ID, 64),
            ],
            SOCIAL_SCIENCE: [
                BookMetadata("Mathematics Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 62),
                BookMetadata("English Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 60),
                BookMetadata("Kitaaba Barataa Afan Oromo Kutaa 11", PRIVATE_CHANNEL_ID, 64),
                BookMetadata("Economics Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 72),
                BookMetadata("Geography Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 73),
                BookMetadata("History Grade 11 Student Textbooks", PRIVATE_CHANNEL_ID, 74),
            ]
        },
        TEACHER_DIR: {
            NATURAL_SCIENCE: [
                BookMetadata("English Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 66), 
                BookMetadata("Mathematics Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 67),
                BookMetadata("Physics Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 68), 
                BookMetadata("Chemistry Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 69),
                BookMetadata("Biology Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 70),
            ],
            SOCIAL_SCIENCE: [
                BookMetadata("English Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 66), 
                BookMetadata("Mathematics Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 67),
                BookMetadata("Economics Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 75), 
                BookMetadata("Geography Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 76),
                BookMetadata("Civic and Ethical Education Grade 11 Teachers Guide", PRIVATE_CHANNEL_ID, 77),
            ]
        }
    },
    
    '12': {
        STUDENT_DIR: {
            NATURAL_SCIENCE: [
                BookMetadata("Biology Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 79), 
                BookMetadata("Chemistry Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 80),
                BookMetadata("It Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 81),
                BookMetadata("English Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 82),
                BookMetadata("Mathematics Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 83),
                BookMetadata("Physics Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 84),
                BookMetadata("Agriculture Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 85),
                BookMetadata("Afaan Oromo Grade 12 Student Text Books", PRIVATE_CHANNEL_ID, 95),
            ],
            SOCIAL_SCIENCE: [
                BookMetadata("English Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 82),
                BookMetadata("Mathematics Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 83),
                BookMetadata("Afaan Oromo Grade 12 Student Text Books", PRIVATE_CHANNEL_ID, 95),
                BookMetadata("History Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 97),
                BookMetadata("Geography Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 98),
                BookMetadata("Economics Grade 12 Student Textbooks", PRIVATE_CHANNEL_ID, 99)
            ]
        },
        TEACHER_DIR: {
            NATURAL_SCIENCE: [
                BookMetadata("Mathematics Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 88), 
                BookMetadata("Physics Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 89),
                BookMetadata("English Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 90), 
                BookMetadata("Chemistry Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 91),
                BookMetadata("Agricultural Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 92), 
                BookMetadata("Biology Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 93),
                BookMetadata("It Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 94),
            ],
            SOCIAL_SCIENCE: [
                BookMetadata("Mathematics Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 88),
                BookMetadata("English Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 90),
                BookMetadata("Economics Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 101),
                BookMetadata("Geography Grade 12 Teachers Guide", PRIVATE_CHANNEL_ID, 102),
            ]
        }
    }
}
def get_dynamic_book_metadata(grade: str, state: str, track: str = "") -> List[BookMetadata]:
    """Retrieves book metadata (name, ID) from the in-memory structure."""
    
    final_track = track if grade in TRACK_GRADES else ''
    
    try:
        grade_data = BOOK_DATA.get(grade, {})
        state_data = grade_data.get(state, {})
        return state_data.get(final_track, [])
    except Exception as e:
        logger.error(f"Data lookup error for G:{grade}, S:{state}, T:{track}: {e}")
        return []

async def delete_history(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    if MESSAGE_HISTORY_KEY in context.user_data:
        try:
            for message_id in context.user_data[MESSAGE_HISTORY_KEY]:
                await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            context.user_data[MESSAGE_HISTORY_KEY] = []
        except Exception as e:
            logger.warning(f"Failed to delete old messages for {chat_id}: {e}")

async def send_and_track(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, reply_markup=None, parse_mode="Markdown", delete_history_flag=False, disable_web_page_preview=False):
    chat_id = update.message.chat_id

    if delete_history_flag:
        await delete_history(chat_id, context)

    sent_message = await update.message.reply_text(
        text,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview
    )

    if MESSAGE_HISTORY_KEY not in context.user_data:
        context.user_data[MESSAGE_HISTORY_KEY] = []

    context.user_data[MESSAGE_HISTORY_KEY].append(sent_message.message_id)
    if update.message.message_id not in context.user_data[MESSAGE_HISTORY_KEY]:
        context.user_data[MESSAGE_HISTORY_KEY].append(update.message.message_id)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    context.user_data[USER_STATE_KEY] = BotState.MAIN
    welcome_message = (
        "Hello! I'm your E-Book bot. 📚\n\n"
        "🎓 Need help studying? Check out [📚 Ethio-Smart Study](https://t.me/EthioSmartStudy_bot) for practice and study tools!\n\n"
        "How can I help you today? Please choose an option from the menu below."
    )
    await send_and_track(update, context, welcome_message, reply_markup=MAIN_MENU_KEYBOARD, delete_history_flag=True)

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    context.user_data[USER_STATE_KEY] = BotState.MAIN
    context.user_data.pop(PENDING_GRADE_KEY, None)
    context.user_data.pop(PENDING_STATE_KEY, None)
    await send_and_track(update, context, "🏠 You are back at the Main Menu. What would you like to do?", reply_markup=MAIN_MENU_KEYBOARD)

async def clear_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    await delete_history(chat_id, context)
    context.user_data.clear() 

    await update.message.reply_text(
        "❌ Session Cleared & Menu Hidden! ❌\n\nTo start fresh, please use the /start command.",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )

async def back_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    current_state = context.user_data.get(USER_STATE_KEY, BotState.MAIN)
    chat_id = update.message.chat_id

    if current_state == BotState.TRACK_SELECTION:
        original_state = context.user_data.pop(PENDING_STATE_KEY, BotState.STUDENT_GRADE)
        context.user_data.pop(PENDING_GRADE_KEY, None)
        context.user_data[USER_STATE_KEY] = original_state
        
        keyboard = STUDENT_GRADE_KEYBOARD if original_state == BotState.STUDENT_GRADE else TEACHER_GRADE_KEYBOARD
        await send_and_track(update, context, "Please select the Grade again.", reply_markup=keyboard)
        return
    
    elif current_state in [BotState.STUDENT_GRADE, BotState.TEACHER_GRADE]:
        await main_menu(update, context)
        return
    
    else: 
        await send_and_track(update, context, "You are already at the Main Menu.", reply_markup=MAIN_MENU_KEYBOARD)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    text = str(update.message.text).strip()
    current_state: BotState = context.user_data.get(USER_STATE_KEY, BotState.MAIN)
    logger.info(f"User {chat_id} | State: {current_state.value} | Sent: {text}")
    
    if text in ["Main Menu 🏠", "/start"]:
        await main_menu(update, context)
        return
    if text == "Clear Menu ❌":
        await clear_menu(update, context)
        return
    if text == "Back ↩️":
        await back_menu(update, context)
        return
    
    if current_state == BotState.MAIN:
        if text == "📚 Get Student Books":
            context.user_data[USER_STATE_KEY] = BotState.STUDENT_GRADE
            await send_and_track(update, context, "Great! Please select the Grade for the Student Books.", reply_markup=STUDENT_GRADE_KEYBOARD)
            return
        elif text == "👨‍🏫 Get Teacher Guides":
            context.user_data[USER_STATE_KEY] = BotState.TEACHER_GRADE
            await send_and_track(update, context, "Great! Please select the Grade for the Teacher Guides.", reply_markup=TEACHER_GRADE_KEYBOARD)
            return
        elif text == "📞 Let's Contact":
            await send_and_track(update, context, CONTACT_INFO, reply_markup=MAIN_MENU_KEYBOARD, disable_web_page_preview=True)
            return
        else:
            await send_and_track(update, context, "Please choose an option from the menu buttons.", reply_markup=MAIN_MENU_KEYBOARD)
            return
            
    elif current_state in [BotState.STUDENT_GRADE, BotState.TEACHER_GRADE]:
        match = re.search(r'Grade\s (\d+)', text)
        if match:
            grade = match.group(1).strip()
            state_dir = STUDENT_DIR if current_state == BotState.STUDENT_GRADE else TEACHER_DIR

            if grade in TRACK_GRADES:
                context.user_data[PENDING_GRADE_KEY] = grade
                context.user_data[PENDING_STATE_KEY] = current_state
                context.user_data[USER_STATE_KEY] = BotState.TRACK_SELECTION
                await send_and_track(
                    update, context,
                    f"You selected Grade {grade}. Please choose your Stream.",
                    reply_markup=TRACK_KEYBOARD
                )
                return
            elif grade in AVAILABLE_GRADES:
                await execute_file_sending(update, context, grade=grade, state=state_dir, track="")
                return
            else:
                keyboard = STUDENT_GRADE_KEYBOARD if current_state == BotState.STUDENT_GRADE else TEACHER_GRADE_KEYBOARD
                await send_and_track(update, context, f"Grade {grade} is not available. Please select a valid grade.", reply_markup=keyboard)
                return
        else:
            keyboard = STUDENT_GRADE_KEYBOARD if current_state == BotState.STUDENT_GRADE else TEACHER_GRADE_KEYBOARD
            await send_and_track(update, context, "Please select a valid grade from the buttons below.", reply_markup=keyboard)
            return
            
    elif current_state == BotState.TRACK_SELECTION:
        track = None
        if NATURAL_SCIENCE in text:
            track = NATURAL_SCIENCE
        elif SOCIAL_SCIENCE in text:
            track = SOCIAL_SCIENCE
            
        grade = context.user_data.get(PENDING_GRADE_KEY)
        original_state: BotState = context.user_data.get(PENDING_STATE_KEY)
        state_dir = STUDENT_DIR if original_state == BotState.STUDENT_GRADE else TEACHER_DIR
        
        if track and grade and original_state:
            await execute_file_sending(update, context, grade=grade, state=state_dir, track=track)
            context.user_data[USER_STATE_KEY] = original_state
            context.user_data.pop(PENDING_GRADE_KEY, None)
            context.user_data.pop(PENDING_STATE_KEY, None)

            keyboard = STUDENT_GRADE_KEYBOARD if original_state == BotState.STUDENT_GRADE else TEACHER_GRADE_KEYBOARD
            await send_and_track(
                update,
                context,
                "Please select another grade or go back.",
                reply_markup=keyboard,
            )
            return
        else:
            await send_and_track(update, context, "Please select a valid Stream or use the navigation buttons.", reply_markup=TRACK_KEYBOARD)
            return
            
    else:
        await main_menu(update, context)


async def execute_file_sending(update: Update, context: ContextTypes.DEFAULT_TYPE, grade: str, state: str, track: str):
    chat_id = update.message.chat_id

    book_category = f"Grade {grade}"
    if track:
        book_category += f" - {track}"

    book_metadata_list = get_dynamic_book_metadata(grade, state, track)

    keyboard = STUDENT_GRADE_KEYBOARD if state == STUDENT_DIR else TEACHER_GRADE_KEYBOARD

    if not book_metadata_list:
        await send_and_track(update, context, f"I don't have any books for {book_category} in this section.", reply_markup=keyboard)
        return

    await send_and_track(update, context, f"Preparing to send {len(book_metadata_list)} files for {book_category} now...", reply_markup=keyboard)

    files_sent_count = 0
    
    for book in book_metadata_list:
        file_name = book.name
        source_chat_id = book.source_chat_id
        message_id = book.message_id
        
        try:
            sent_message = await context.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=source_chat_id, 
                message_id=message_id, 
                caption=f"📚 {file_name}", 
                parse_mode="Markdown",
                disable_notification=True
            )
            if MESSAGE_HISTORY_KEY not in context.user_data:
                context.user_data[MESSAGE_HISTORY_KEY] = []
            context.user_data[MESSAGE_HISTORY_KEY].append(sent_message.message_id)

            files_sent_count += 1
            logger.info(f"Copied document: {file_name} (Msg ID: {message_id})")
            
        except Exception as e:
            logger.error(f"Failed to copy document {file_name} (Msg ID: {message_id}): {e}")
            await send_and_track(
                update, context, 
                f"❌ Failed to send file {file_name}.\n\n"
                f"Troubleshoot: Ensure the bot is an administrator in the channel and the Message ID {message_id} is correct.", 
                reply_markup=keyboard
            )
            
    await send_and_track(
        update, context,
        f"✅ Finished! Sent {files_sent_count} files for {book_category}.\n\nThanks for using E-Books what's next ?",
        reply_markup=keyboard
    )

async def help_command(update:Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_message = (
        "📚 Textbook Bot Help 📚\n\n"
        "Use the Main Menu 🏠 button to navigate to:\n"
        "1. Student Books (by Grade)\n"
        "2. Teacher Guides (by Grade)\n"
        "3. Contact Info\n\n"
        "🎓 *Looking for study tools?* Practice and study with [📚 Ethio-Smart Study](https://t.me/EthioSmartStudy_bot)!\n\n"
        "Navigation:\n"
        "↩️ Back: Go to the previous menu.\n"
        "🏠 Main Menu: Go to the primary selection screen.\n"
        "❌ Clear Menu: Deletes bot messages and hides the keyboard (resets session)."
    )
    await send_and_track(update, context, help_message, reply_markup=MAIN_MENU_KEYBOARD)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

if __name__ == "__main__":
    logger.info("Starting bot in polling mode...")

    app = Application.builder().token(TOKEN).read_timeout(120.0).write_timeout(120.0).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("menu", start_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)

    logger.info("Bot is running with polling... Press Ctrl+C to stop.")
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped gracefully.")
