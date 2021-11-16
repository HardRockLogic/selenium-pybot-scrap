from tg_token import TOKEN
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
update = False
price_range = False


def update_all():
    global colours
    colours = None
    global price
    price = None
    global size
    size = None
    global update
    update = False
    global price_range
    price_range = False


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    functional_buttons = ['\U0001F50E Start search', 'Update page', 'How to use me?']
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*functional_buttons)

    await message.reply('Wasap mate, lets find some staff', reply_markup=keyboard)


# Waiting for color input from user with regular expression handler
@dp.message_handler(regexp=r'([А-Яа-я]{1,}(,|$))+')
async def search_re_colour(message: types.Message):
    global colours
    colours = message.text
    if ', ' in colours:
        intermediate = colours[:-1].split(', ')
    elif ' ' in colours:
        intermediate = colours[:-1].split(' ')
    else:
        intermediate = colours[:-1].split(',')

    colours = list(map(lambda x: x.replace('й','е'), intermediate))

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
@dp.message_handler(regexp=r'^(\d{4})$')
async def search_re_price(message: types.Message):
    global price
    price = int(message.text)
    redefined = 'Ценовой лимит: ' + message.text
    await message.reply(f'{redefined}')


# Waiting for price range input
@dp.message_handler(regexp=r'^((\d{4})((\s-\s)|(-))(\d{4}))$')
async def price_range(message: types.Message):
    global price_range
    tup_of_prices = tuple(map(lambda a: int(a.strip()), message.text.split('-')))

    if tup_of_prices[0] >= tup_of_prices[1]:
        await message.reply('invalid range: second elem could not exceed the first elem')
    else:
        price_range = (True, tup_of_prices)
        redefined = 'Диапазон: ' + message.text
        await message.reply(f'{redefined}')


# # Waiting for size input
@dp.message_handler(regexp=r'^(\d{1,2}((,|\.)\d)?)$')
async def search_re_size(message: types.Message):
    global size
    if ',' in message.text:
        size = message.text.replace(',', '.')
    else:
        size = float(message.text)
    redefined = 'Ваш размер: ' + message.text
    await message.reply(f'{redefined}, {size}')


@dp.message_handler(Text(equals='Update page'))
async def update_flag(message: types.Message):
    global update
    update = True
    await message.answer('Page will be refreshed after pressing search button\n'
                         'It will take a little bit more than usual\n\n'
                         'I recommend doing it several times a day at most')


@dp.message_handler(Text(equals='How to use me?'))
async def update_flag(message: types.Message):

    await message.answer('Just jot down any colour (or colours divided by comma or space) in plural or single form,'
                         'then type price limit and press \U0001F50E <b>Start search</b>\n\n'
                         'You also can search only by colour(s) or price (or without any sorting option, '
                         'but there are <i>too much</i> items)\n\n'
                         'Btw the <b>Update page</b> button used to refresh data about items in stock, so'
                         'there is no need to do this more than once a day')


@dp.message_handler(Text(equals='\U0001F50E Start search'))
async def searching(message: types.Message()):
    color = 'Image'
    is_available = False
    counter = 0
    await message.answer('Це може зайняти якийсь час')

    # Condition for both, colors and price limit defined by user
    if price and colours is not None:
        for key, value in getData(update=update, price_range_flag=price_range).items():
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

        update_all()

    # Condition for only price defined by user
    elif (colours is None) and price is not None:
        for key, value in getData(update=update, price_range_flag=price_range).items():
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

        update_all()

    # Condition for only colour(s) defined by user
    elif (price is None) and colours is not None:
        for key, value in getData(update=update, price_range_flag=price_range).items():
            for colour in colours:
                if value[1].find(colour) != -1:
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

        update_all()

    # Condition for no sorting options
    else:  #price and colours is None:
        for key, value in getData(update=update, price_range_flag=price_range).items():
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

        update_all()


@dp.message_handler(commands=['help'])
async def start_command(message: types.Message):
    await message.reply('Тут ти можеш вибратні нові чуні зі скидоном, відсортувати іх за кольором, розміром, та ціною\n\n'
                        '(Та я ще в розробці)')


if __name__ == '__main__':
    executor.start_polling(dp)


