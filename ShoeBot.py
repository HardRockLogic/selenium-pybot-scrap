from tg_token import TOKEN
import aiogram.dispatcher.webhook
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.utils import executor
from aiogram.utils.markdown import hlink, hbold
from main import getData, filter_size_by_url
import time

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


colours = None
price = None
size = None


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    functional_buttons = ['\U0001F50E Почати пошук', 'Обери колір', 'Ціновий ліміт']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functional_buttons)

    await message.reply('blyaaaa', reply_markup=keyboard)


# Waiting for color input from user with regular expression handler
@dp.message_handler(regexp=r'([А-Яа-я]{1,},)+')
async def search_re_colour(message: types.Message):
    global colours
    colours = message.text
    colours = colours[:-1].split(',')

    temporary_list = []
    for item in colours:
        if item[0].isupper():
            temporary_list.append(f'{item.lower()}')
        else:
            temporary_list.append(f'{item.capitalize()}')

    for temporary in temporary_list:
        colours.append(temporary)

    redefined = 'Ваш цвет: ' + message.text
    await message.reply(f'{redefined}')


# Waiting for price limit input
@dp.message_handler(regexp='^(\d{4})$')
async def search_re_price(message: types.Message):
    global price
    price = int(message.text)
    redefined = 'Ценовой лимит: ' + message.text
    await message.reply(f'{redefined}')


# # Waiting for size input
@dp.message_handler(regexp='^(\d{1,2}((,|\.)\d)?)$')
async def search_re_size(message: types.Message):
    global size
    if ',' in message.text:
        size = message.text.replace(',', '.')
    else:
        size = float(message.text)
    redefined = 'Ваш размер: ' + message.text
    await message.reply(f'{redefined}, {size}')


# @dp.message_handler(Text(equals='Обери колір'))
# async def color_filter(message: types.Message()):
#     color_buttons = ['Чорний', 'Білий', 'Салатовий']
#     color_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     color_keyboard.add(*color_buttons)
#
#     await message.answer('Ok', reply_markup=color_keyboard)


@dp.message_handler(Text(equals='\U0001F50E Почати пошук'))
async def searching(message: types.Message()):
    color = 'Черные'
    is_available = False
    counter = 0
    await message.answer('Це може зайняти якийсь час')

    # Condition for both, colors and price limit defined by user
    if price and colours is not None:
        for key, value in getData().items():
            for colour in colours:
                if int(value[0]) <= price and value[1].find(colour) != -1:
                    output = f'{hlink(color, value[2])}\n' \
                             f'{hlink(value[1], key)}\n' \
                             f'{hbold(value[0])} <b>грн</b>'
                    time.sleep(0.5)
                    await message.answer(output)
                    is_available = True
                    counter += 1

        if is_available is False:
            await message.answer('No such items :( ...')
        else:
            await message.answer(f'{counter} items found :)')

    # Condition for only price defined by user
    if (colours is None) and price is not None:
        for key, value in getData().items():
            if int(value[0]) <= price:
                output = f'{hlink(color, value[2])}\n' \
                         f'{hlink(value[1], key)}\n' \
                         f'{hbold(value[0])} <b>грн</b>'
                time.sleep(0.5)
                await message.answer(output)
                is_available = True
                counter += 1

        if is_available is False:
            await message.answer('No such items :( ...')
        else:
            await message.answer(f'{counter} items found :)')



@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):
    await message.reply('Тут ти можеш вибратні нові чуні зі скидоном, відсортувати іх за кольором, розміром, та ціною\n\n'
                        '(Та я ще в розробці)')


if __name__ == '__main__':
    executor.start_polling(dp)

# @dp.message_handler(Text(equals='Почати пошук'))
# async def searching(message: types.Message()):
#     #discount_dict = getData()
#     price = 3000
#     color = 'Черные'
#     color2 = 'синие'
#     #output = []
#     for key, value in getData().items():
#         if int(value[0]) <= price and color2 in value[1]:
#             output = f'{hlink(color, value[2])}\n' \
#                      f'{hlink(value[1], key)}\n' \
#                      f'{hbold(value[0])} <b>грн</b>'
#             # output[0] = f'{hlink(value[1], key)}'
#             # output[1] = f'{value[0]}'
#             time.sleep(0.5)
#             await message.answer(output)
