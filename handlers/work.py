from aiogram import Router, F, Bot
from aiogram.types import  CallbackQuery, FSInputFile
from sqlalchemy import select
from keyboards.for_main_func import  get_keyboard_dostavka
from keyboards.for_registration import get_keyboard_clear,get_keyboard_admin,get_keyboard_back_work
import asyncio
from sqlalchemy.ext.asyncio import  AsyncSession
from db.user import User, Cart, Product
import re
import csv


router = Router()


@router.callback_query(F.data == "back_work")
async def back_work (callback: CallbackQuery):
    await callback.message.answer("Админка", reply_markup=get_keyboard_admin())

@router.callback_query(F.data == "spam")
async def spam(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    cart_sel = select(Cart).where(Cart.sum >= 1500)
    cart_result = await session.execute(cart_sel)
    cart = cart_result.scalars()
    cart_spam = {i.chatId: i.sum for i in cart}

    for chatId in cart_spam:
        await bot.send_message(int(chatId), text="Завтра будет доставка с 11:00 до 17:00. Если вы готовы принять, то выберите кнопку \"Доставка\" и уточните свой адрес", reply_markup=get_keyboard_dostavka())

@router.callback_query(F.data == "get_file_dostavka")
async def get_file_dostavka(callback: CallbackQuery, session: AsyncSession):
    user_sel = select(User)
    result = await session.execute(user_sel)
    user = result.scalars().all()
    # Создание файла с пользователями которые войдут в доставку
    with open('clients_car.csv', "w", newline="") as file:
        writer = csv.writer(file, delimiter="|")
        filed = ["Номер телефона", "Имя", "Сумма", "Адрес"]
        writer.writerow(filed)

        for i in user:
            carts = i.cart

            for c in carts:

                if(c.sum >= 1500):
                    writer.writerow([i.phone, i.name, c.sum, i.address])


@router.callback_query(F.data == "get_cart_user")
async def get_cart_user(callback: CallbackQuery, session: AsyncSession, bot: Bot):
    product_sel = select(Product)
    result = await session.execute(product_sel)
    product = result.scalars().all()
    # Сбор товара - вывод всех забронированных товаров у которых нету "Собрано"
    for i in range(len(product)):
        check_product_in_cart = bool(re.search("Собрано", product[i].description))
        if(check_product_in_cart == False):
            photo = product[i].photo
            send_photo = FSInputFile(f"C:\\folder\\" + photo)
            await callback.message.answer_photo(photo=send_photo,
                                            caption="Цена {price} Р\n\n{description}\n\n{dataCreate}".format(
                                                price=product[i].price, description=product[i].description,
                                                dataCreate=product[i].dataCreatePost))
            product[i].description += " Собрано"
            await session.commit()

    await callback.message.answer("В меню", reply_markup=get_keyboard_back_work())



@router.callback_query(F.data == "check_dostavki")
async def delete_cart(callback: CallbackQuery, session: AsyncSession):
    cart_sel = select(Cart).where(Cart.sum >= 1500)
    cart_result = await session.execute(cart_sel)
    cart = cart_result.scalars()
    # Вывод товаров которые были доставлен
    for i in cart:
        summa = 0

        for stmt in i.product:
            check_product_in_cart = bool(re.search("Собрано", stmt.description))

            if(check_product_in_cart == True and i.id == stmt.cart_id):
                summa += int(stmt.price)

        if(summa >= 1500):
            cart_info = "{chatId}\n\n{name} {phone}. Сумма корзины: {sum}".format(chatId=i.user.chatId, name=i.user.name, phone=i.user.phone, sum=summa)
            await callback.message.answer(cart_info, reply_markup=get_keyboard_clear())

    await callback.message.answer("В меню", reply_markup=get_keyboard_back_work())


@router.callback_query(F.data == 'clear_cart')
async def clear_cart(callback: CallbackQuery, session: AsyncSession):
    id = callback.message.text.split("\n\n")[0]
    cart_sel = select(Cart).where(Cart.chatId == int(id))
    cart_result = await session.execute(cart_sel)
    cart = cart_result.scalar()
    # Удаление товаров выведенных прошлой функцией, удалять список нужно вручную, т.к. могут быть форс мажоры
    for i in cart.product:
        check_product_in_cart = bool(re.search("Собрано", i.description))

        if (check_product_in_cart == True):
            cart.sum -= int(i.price)
            await session.delete(i)
    cart.knox = 3
    cart.user.address = None
    await session.commit()

