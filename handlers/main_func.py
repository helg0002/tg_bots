from aiogram import Router, F, Bot, exceptions
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from sqlalchemy import select
from keyboards.for_main_func import get_keyboard_main, get_keyboard_back, get_keyboard_buy, get_keyboard_address, get_keyboard_refusal
from aiogram.fsm.context import FSMContext
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from db.user import User, Cart, Product
from filters.type_chat import ChatTypeFilter
import re
import os
from dotenv import load_dotenv
from lexicon.lexicon import LEXICON_MAIN
from keyboards.for_view_cart import ViewProduct, view_product



# async def check_data_handler(request: Request):
#     bot: Bot = request.app["bot"]
#
#     data = await request.post()  # application/x-www-form-urlencoded
#     try:
#         data = safe_parse_webapp_init_data(token='6445418329:AAHeVGSI5hQuLADjc42HsH1GAM3H2DEzmxE', init_data=data["_auth"])
#     except ValueError:
#         return json_response({"ok": False, "err": "Unauthorized"}, status=401)
#     return json_response({"ok": True, "data": data.user.dict()})


# Загрузка env
load_dotenv()

router = Router()
# Состояния
class FSM(StatesGroup):
    address = State()
    msg = State()


@router.callback_query(F.data == "get_rules" )
async def get_rules(callback: CallbackQuery):
    await callback.message.edit_text(LEXICON_MAIN['rules'], parse_mode="html", reply_markup=get_keyboard_back())




@router.callback_query(F.data == "back")
async def back (callback: CallbackQuery, state: FSMContext, bot:Bot):
    message_id = await state.get_data()
    print(message_id)
    print(len(message_id))
    if(len(message_id) > 0):
        for i in message_id["msg_id"]:
            await bot.delete_message(chat_id=callback.message.chat.id, message_id=i)
        await state.clear()
    await callback.message.edit_text(LEXICON_MAIN['main'],
                             reply_markup=get_keyboard_main(), parse_mode="html")



@router.message(F.photo, ChatTypeFilter(chat_type=["group", "supergroup"]))
async def cmd_go(message: Message):
    to_id = os.getenv("ID_CHANNEL")
    try:
        await message.copy_to(to_id, message.chat.id, message.message_thread_id, reply_markup=get_keyboard_buy())
    except exceptions.TelegramRetryAfter as err:
        await asyncio.sleep(30)
        await cmd_go(message)



@router.callback_query(F.data == "buy")
async def buy (callback: CallbackQuery, session: AsyncSession, bot: Bot):
    try:
        cart_sel = select(Cart).where(Cart.chatId == callback.from_user.id)
        result = await session.execute(cart_sel)
        cart = result.scalar()
        if (cart == None):
            await callback.answer(LEXICON_MAIN['val_reg'], show_alert=True)
            return
        # Получение данных о товаре
        cost = re.findall('\d+', callback.message.caption)[0]
        results_quantity = re.findall('\d+', " ".join(re.findall('В наличии{1}.+?\d+|Наличие{1}.+?\d+', callback.message.caption)))
        results_caption = callback.message.caption.split('\n', 6)
        caption = [x for x in results_caption if x][1]

        if results_quantity == []:
            quantity = 1
        else:
            quantity = int(results_quantity[0])

        #Сохранение фото
        file_id = callback.message.photo[-1].file_id
        file = await bot.get_file(file_id)
        destination = fr"C:\folder\{file_id}.jpg"
        await bot.download(file, destination)
        photo = file_id + ".jpg"


        user = cart.user

        await session.merge(Product(description=caption + " " + user.name + " " + user.phone , price=cost, dataCreatePost=callback.message.date, photo=photo, cart_id =cart.id))

        cart.sum += int(cost)
        if cart.dataCreate is None: cart.dataCreate = callback.message.date
        await session.commit()
        await session.close()
        if quantity == 1:
            await callback.message.delete()
        else:
            quantity -= 1
            await callback.message.edit_caption(
                caption="Цена " + cost + "Р\n\n" + caption + "\n\n" + "В наличии {quantity}шт".format(cost=cost,
                                                                                                      caption=caption,
                                                                                                      quantity=quantity),
                reply_markup=get_keyboard_buy())


    except exceptions.TelegramBadRequest as err:
        await callback.answer("Товар был кем-то забронирован")


# @router.callback_query(F.data == "view_cart")
# async def view_cart(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
#     cart_sel = select(Cart).where(Cart.chatId == callback.from_user.id)
#     result_cart = await session.execute(cart_sel)
#     cart = result_cart.scalar()
#     await callback.message.delete()
#     msg_id = []
#     # Вывод забронированного поста пользователю
#     for i in cart.product:
#         photo = i.photo
#         send_photo = FSInputFile(f"C:\\folder\\" + photo)
#         msg = await callback.message.answer_photo(photo=send_photo, caption="Цена {price} Р\n\n{description}\n\n{dataCreate}".format(price=i.price, description=i.description, dataCreate=i.dataCreatePost), reply_markup=get_keyboard_refusal())
#         msg_id.append(msg.message_id)
#     await state.update_data(msg_id=msg_id)
#
#     await callback.message.answer("Сумма вашего заказа: " + str(cart.sum) + " Р", reply_markup=get_keyboard_back())
#     await callback.answer()


@router.callback_query(F.data == "view_cart")
async def view_cart(callback: CallbackQuery, session: AsyncSession, state: FSMContext, bot:Bot):
    try:
        cart_sel = select(Cart).where(Cart.chatId == callback.from_user.id)
        result_cart = await session.execute(cart_sel)
        cart = result_cart.scalar()
        await callback.message.delete()
        msg_id = []
        media = []
        caption = []
        product_id = []
        msg_media_list = []
        # Вывод забронированного поста пользователю

        for i in cart.product:
            photo = i.photo
            send_photo = FSInputFile(f"C:\\folder\\" + photo)
            media.append(InputMediaPhoto(media=send_photo, caption="Цена {price} Р\n\n{description}\n\n{dataCreate}".format(price=i.price, description=i.description, dataCreate=i.dataCreatePost)))
            caption.append(str(len(media)) + ". -- Цена {price} Р\n{description}".format(price=i.price, description=i.description))
            product_id.append(i.id)

        for i in range(0, len(media), 10):
            media_group = media[i:i + 10]
            msg_media_group = await callback.message.answer_media_group(media=media_group)
            for i in range(len(msg_media_group)):
                media_group_msg_id = msg_media_group[i].message_id
                msg_media_list.append(media_group_msg_id)
                msg_id.append(media_group_msg_id)

        btn = view_product(caption, product_id, msg_media_list)

        if(len(media) != 0):
            msg_btn = await callback.message.answer(text="Здесь вы можете отказаться от брони.\n\nНе более 3-х отказов до следующей доставки", reply_markup=btn)
            msg_id.append(msg_btn.message_id)

        sum = await callback.message.answer("Сумма вашего заказа: " + str(cart.sum) + " Р", reply_markup=get_keyboard_back())
        await state.update_data(msg_id=msg_id, sum=sum.message_id)
    except exceptions.TelegramServerError as err:
        await callback.answer("Пожалуйста подождите")
        await view_cart(callback, session, state, bot)



@router.callback_query(F.data == "dostavka")
async def dostavka(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    cart_sel = select(Cart).where(Cart.chatId == callback.message.chat.id)
    cart_result = await session.execute(cart_sel)
    cart = cart_result.scalar()
    if(cart.sum >= 1500):
        msg = await callback.message.edit_text("Введите свой адрес:")
        await state.set_state(FSM.address)
        await state.update_data(msg_id=msg.message_id)


@router.message(FSM.address)
async def load_name(message: Message, state: FSMContext, bot:Bot):
    data = message.text
    msg = await state.get_data()
    await state.update_data(address=data)
    await message.delete()
    await bot.edit_message_text(text="Ваш адрес:  " + data, chat_id = message.chat.id, message_id=msg["msg_id"], reply_markup=get_keyboard_address())


@router.callback_query(F.data == "add_address_bd")
async def save_address(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    user_sel = select(User).where(User.chatId == callback.from_user.id)
    result_user = await session.execute(user_sel)
    user = result_user.scalars().one()
    user.address = user_data["address"]
    await session.commit()
    await session.close()
    await callback.message.edit_text(LEXICON_MAIN['val_adr'], reply_markup=get_keyboard_back())
    await state.clear()





@router.callback_query(F.data == "reply_address")
async def rename(callback: CallbackQuery, state: FSMContext):
        await callback.message.edit_text(text="Введите адрес заново:")
        await state.set_state(FSM.address)

# @router.callback_query(F.data == "refusal")
# async def refusal(callback: CallbackQuery, session: AsyncSession):
#     to_id = -1001967447696
#
#     results_caption = callback.message.caption.split('\n', 6)
#     caption = [x for x in results_caption if x][1]
#
#     cart_sel = select(Cart).where(Cart.chatId == callback.from_user.id)
#     result_cart = await session.execute(cart_sel)
#     cart = result_cart.scalars().one()
#
#     if cart.knox > 0:
#         product_sel = select(Product).where(Product.cart_id == cart.id,Product.description == caption)
#         result_product = await session.execute(product_sel)
#         product = result_product.scalars().first()
#         cart.sum -= int(product.price)
#         cart.knox -= 1
#         await session.delete(product)
#         await session.commit()
#
#         # Занести Product.photo и им подобные в функцию, чтобы 10 раз не прописывать
#         await callback.message.copy_to(chat_id=to_id)
#         await callback.message.delete()
#     else:
#         await callback.answer("Залупу на воротник. Больше 3-х до следующей доставки нельзя")


# @router.callback_query(F.data == "refusal")
# async def refusal(callback: CallbackQuery, session: AsyncSession):
#     to_id = os.getenv("ID_CHANNEL_REFUSAL")
#     results_caption = callback.message.caption.split('\n', 6)
#     caption = [x for x in results_caption if x][1]
#
#     product_sel = select(Product).where(Product.description == caption)
#     result_product = await session.execute(product_sel)
#     product = result_product.scalars().first()
#
#     if product.cart.knox > 0 and product.cart.chatId == int(callback.message.chat.id):
#         if(bool(re.search("Собрано", product.description))):
#             await callback.answer("От собранного товара нельзя отказаться", show_alert=True)
#             return
#
#         product.cart.sum -= int(product.price)
#         product.cart.knox -= 1
#
#         await session.delete(product)
#         await session.commit()
#         await callback.message.copy_to(chat_id=to_id)
#         await callback.message.delete()
#     else:
#         await callback.answer("Больше 3-х до следующей доставки нельзя", show_alert=True)

@router.callback_query(ViewProduct.filter())

async def refusal(callback: CallbackQuery, session: AsyncSession, callback_data: ViewProduct, bot: Bot, state: FSMContext):
    await asyncio.sleep(1)
    caption = callback.message.reply_markup.inline_keyboard
    to_id = os.getenv("ID_CHANNEL_REFUSAL")
    btn_id = []
    btn_text = []
    btn_msg = []
    fsm = await state.get_data()

    product_sel = select(Product).where(Product.id == callback_data.id)
    result_product = await session.execute(product_sel)
    product = result_product.scalars().first()

    print(fsm['msg_id'])
    if product.cart.knox > 0 and product.cart.chatId == int(callback.message.chat.id):
        if("Собрано" in product.description):
            await callback.answer("От собранного товара нельзя отказаться", show_alert=True)
            return

        product.cart.sum -= int(product.price)
        product.cart.knox -= 1

        for i in caption:
            cal_data = i[0].callback_data.split(":")
            id = int(cal_data[2])
            msg_id = int(cal_data[3])

            if (id == product.id):
                await bot.delete_message(chat_id=callback.message.chat.id, message_id=msg_id)
                fsm['msg_id'].remove(msg_id)

            if (id != product.id):
                btn_id.append(id)
                btn_text.append(i[0].text)
                btn_msg.append(msg_id)

        btn = view_product(btn_text, btn_id, btn_msg)

        photo = product.photo
        send_photo = FSInputFile(f"C:\\folder\\" + photo)
        await bot.send_photo(chat_id=to_id, photo=send_photo, caption="Цена {price} Р\n\n{description}\n\n{dataCreate}".format(price=product.price, description=product.description, dataCreate=product.dataCreatePost), reply_markup=get_keyboard_refusal())
        await session.delete(product)
        await session.commit()

        await callback.message.edit_reply_markup(reply_markup=btn)

        await bot.edit_message_text("Сумма вашего заказа: " + str(product.cart.sum) + " Р", callback.message.chat.id, fsm["sum"], reply_markup=get_keyboard_back())
    else:
        await callback.answer("Больше 3-х до следующей доставки нельзя", show_alert=True)
   #
   #
   #
   # class colors:
   #          green = '\x1b[32m'
   #          reset = '\x1b[0m'
   #          red = '\x1b[31m'
   #          black = '\x1b[30m'
   #          yellow = '\x1b[33m'
   #          blue = '\x1b[34m'
   #          magenta = '\x1b[35m'
   #          cyan = '\x1b[36m'
   #          white = '\x1b[37m'
   #          bg_red = '\x1b[41m'
   #          bg_green = '\x1b[42m'
   #
   #      def diff_string(str1: str, str2: str):
   #          l1 = len(str1)
   #          l2 = len(str2)
   #          rst1 = rst2 = ""
   #          for a, b in zip(str1, str2):
   #              color = colors.red if a != b else colors.green
   #              rst1 += color + a + colors.reset
   #              rst2 += color + b + colors.reset
   #          if l1 > l2:
   #              rst1 += colors.bg_red + str1[l2:] + colors.reset
   #              rst2 += colors.bg_red + " " * (l1 - l2) + colors.reset
   #          elif l1 < l2:
   #              rst1 += colors.bg_red + " " * (l2 - l1) + colors.reset
   #              rst2 += colors.bg_red + str2[l1:] + colors.reset
   #          return rst1, rst2
   #
   #      rst1, rst2 = diff_string(caption.rstrip(), product.description.rstrip())
   #      print(f'str2:::\n{rst2}')
   #      print(f'str1:::\n{rst1}')


