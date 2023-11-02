from aiogram import Router, F, Bot, exceptions
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from keyboards.for_registration import get_keyboard, get_keyboard_admin
from aiogram.fsm.context import FSMContext
from keyboards.for_main_func import get_keyboard_main
from sqlalchemy import select
from db.user import User, Cart
from sqlalchemy.ext.asyncio import  AsyncSession
import re
import os
from dotenv import load_dotenv
from lexicon.lexicon import LEXICON_REG

class FSM_name(StatesGroup):
    name = State()
    phone = State()
    work = State()
    id = State()

router = Router()
load_dotenv()



@router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    # Хеш и соль нет смысла, взломают не велика потеря, но мог бы

    to_id = os.getenv("ID_ADMIN")
    user_sel = select(User).where(User.chatId == message.chat.id)
    result = await session.execute(user_sel)
    user = result.scalar()
    if(message.chat.id == int(to_id)):
        await message.answer("Админка", reply_markup=get_keyboard_admin())
    elif(user == None):
        msg = await message.answer(LEXICON_REG["/start"])
        await state.update_data(msg_id=msg.message_id)

        await state.update_data(chatId=message.chat.id)
        await state.update_data(check=0)
        await state.set_state(FSM_name.name)
        await message.delete()

    else:
        await message.answer(text=LEXICON_REG['hello'].format(name=user.name),
                                      reply_markup=get_keyboard_main())






@router.callback_query(F.data == "add_name_bd")
async def save_name(callback: CallbackQuery, state: FSMContext, session: AsyncSession ):
    user_data = await state.get_data()

    if (user_data["check"]) == 0:
        msg = await callback.message.edit_text("Приятно познакомиться. Теперь, пожалуйста введите номер телефона:")
        await state.update_data(check=1, msg_id=msg.message_id)

        await state.set_state(FSM_name.phone)
    else:
        await session.merge(User(chatId=user_data['chatId'], name=user_data['name'], phone=user_data['phone'], address='none'))
        await session.merge(Cart(chatId=user_data['chatId'], sum=0, knox=3))
        await session.commit()
        await session.close()
        await state.clear()
        await callback.message.edit_text(text=LEXICON_REG['hello'].format(name=user_data['name']), parse_mode="html", reply_markup=get_keyboard_main())


@router.callback_query(F.data == "reply_step_one")
async def rename(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    if (user_data["check"]) == 0:
        await callback.message.edit_text(text="Введите ваше имя заново:")
        await state.set_state(FSM_name.name)
    else:
        await callback.message.edit_text("Введите номер телефона заново:")
        await state.set_state(FSM_name.phone)


@router.message(FSM_name.name)
async def load_name(message: Message, state: FSMContext, bot: Bot):
    data = re.findall('[А-я]+', message.text)
    msg = await state.get_data()
    try:
        if(bool(data) != True):
            print("Залупа")
            await message.delete()
            await bot.edit_message_text(text=LEXICON_REG["val_name"], chat_id=message.chat.id, message_id=msg["msg_id"])
            return
        if(len(data[0]) < 3 or len(data[0]) > 12):
            print(len(data[0]))
            await message.delete()
            await bot.edit_message_text(text=LEXICON_REG["val_name"], chat_id=message.chat.id, message_id=msg["msg_id"])
            return

        await message.delete()
        await state.update_data(name=data[0])
        message_id = await state.get_data()
        await bot.edit_message_text(text="Ваше имя:  " + data[0], chat_id=message.chat.id, message_id=message_id['msg_id'], reply_markup=get_keyboard())

    except exceptions.TelegramBadRequest as err:
        return



@router.message(FSM_name.phone)
async def load_phone(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    data = re.findall('((7|8)\D*\d{3}\D*\d{3}\D*\d{2}\D*\d{2})',message.text)
    print("111111111   ",len(data))
    message_id = await state.get_data()

    if (len(data) == 0):
        await message.delete()
        await bot.edit_message_text(text=LEXICON_REG["val_tel"], chat_id=message.chat.id,message_id=message_id['msg_id'])
        return
    phone = data[0][0]

    if(len(phone) != 11):
        await message.delete()
        await bot.edit_message_text(text=LEXICON_REG["val_tel"], chat_id=message.chat.id, message_id=message_id['msg_id'])
        return
    await state.update_data(phone=phone)
    await message.delete()
    await bot.edit_message_text(text="Ваш номер телефона " + phone, chat_id=message.chat.id, message_id=message_id['msg_id'], reply_markup=get_keyboard())

