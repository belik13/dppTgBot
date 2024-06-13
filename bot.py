from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaDocument

from app import *

#support agent data
api_id = 27017711
api_hash = 'c0d7b96cc99c3c0c15048625ff17afbf'
entity = 'bot'
bot_token = "7388607968:AAGGLmsktgT_rTJV_e9D3fd6v-X6oWcQ41E"

bot = TelegramClient(entity, api_id, api_hash)
bot.start(bot_token=bot_token)

input_size = 7
model = new_model(input_size)


async def get_username_from_message(message):
    if isinstance(message.sender_id, int):
        user = await bot.get_entity(message.sender_id)
        username = user.username
        return username
    return None


async def get_file_name_from_message(message):
    if message.media and isinstance(message.media, MessageMediaDocument):
        file_name = message.media.document.attributes[0].file_name
        return file_name
    return None


async def start(event):
    await event.reply('Привет, я сделаю отчет о соосности колонн по облаку точек в формате .pts\n'
                      'Команды:\n'
                      '/start - Выводит это сообщение\n'
                      '/upload - Загружает один файл, файл и команда должны быть одним сообщением\n'
                      '/report - Выводит отчет, при первом запуске может долго работать\n'
                      '/myfiles - Выводит список загруженых файлов\n'
                      '/delete - Удаляет файл\n'
                      'Команды /report и /delete должны через пробел содержать название целевого файла\n')


async def upload(event):
    # await event.reply(event.text)
    filename = await get_file_name_from_message(event)
    if filename is None:
        await event.reply('Не обнаружен файл')
        return None

    if not filename.endswith('.pts'):
        await event.reply('Неверный формат файла')
        return None

    username = await get_username_from_message(event)

    if not os.path.exists(f"data/{username}"):
        # Если папка отсутствует, создаем её
        os.makedirs(f"data/{username}")

    if os.path.exists(f"data/{username}/{filename}"):
        await event.reply("Файл с таким именем уже загружен")
        return None

    with open(f'data/{username}/{filename}', 'wb') as fd:
        async for chunk in bot.iter_download(event.media):
            fd.write(chunk)

    await event.reply("Файл успешно загружен")


async def my_files(event):
    username = await get_username_from_message(event)

    if not os.path.exists(f"data/{username}"):
        # Если папка отсутствует, создаем её
        os.makedirs(f"data/{username}")

    files = [f for f in os.listdir(f"data/{username}") if os.path.isfile(os.path.join(f"data/{username}", f))]

    if len(files) == 0:
        await event.reply("У вас нет загруженных файлов")
        return None

    ans = 'Ваши файлы:'
    for file in files:
        if file.endswith('.pts'):
            ans = ans + '\n' + file

    await event.reply(ans)


async def delete_file(event):
    username = await get_username_from_message(event)

    if not os.path.exists(f"data/{username}"):
        # Если папка отсутствует, создаем её
        os.makedirs(f"data/{username}")

    cmd_list = event.text.split(' ')
    if len(cmd_list) != 2:
        await event.reply("Команда /delete должна содержать имя одного фала через пробел после команды")
        return None

    filename = cmd_list[1]
    if not filename.endswith(".pts"):
        await event.reply("Файл должен быть с расширением .pts")
        return None

    filename_txt = filename.rsplit('.', 1)[0] + '.txt'

    if os.path.exists(f"data/{username}/{filename}"):
        os.remove(f"data/{username}/{filename}")
        if os.path.exists(f"data/{username}/{filename_txt}"):
            os.remove(f"data/{username}/{filename_txt}")
        await event.reply(f"Файл {filename} успешно удален")
    else:
        await event.reply("Такого файла не существует")


async def report(event):
    username = await get_username_from_message(event)

    if not os.path.exists(f"data/{username}"):
        # Если папка отсутствует, создаем её
        os.makedirs(f"data/{username}")

    cmd_list = event.text.split(' ')
    if len(cmd_list) != 2:
        await event.reply("Команда /report должна содержать имя одного фала через пробел после команды")
        return None

    filename = cmd_list[1]
    if not filename.endswith(".pts"):
        await event.reply("Файл должен быть с расширением .pts")
        return None

    filename_txt = filename.rsplit('.', 1)[0] + '.txt'

    if os.path.exists(f"data/{username}/{filename_txt}"):
        with open(f"data/{username}/{filename_txt}", 'r') as file:
            content = file.read()
            await event.reply(content)
            return None

    if not os.path.exists(f"data/{username}/{filename}"):
        await event.reply("Такого файла нет")
        return None

    try:
        rep = analyze_alignment(f'data/{username}/{filename}', model, input_size)
    except:
        await event.reply("Произошла ошибка, проверьте загруженый файл")
        return None

    with open(f"data/{username}/{filename_txt}", 'w') as file:
        file.write(rep)
    await event.reply(rep)


@bot.on(events.NewMessage)
async def handle_new_message(event):
    if event.raw_text.startswith('/report'):
        await report(event)
    elif event.raw_text == '/start':
        await start(event)
    elif event.raw_text == '/upload':
        await upload(event)
    elif event.raw_text == '/myfiles':
        await my_files(event)
    elif event.raw_text.startswith('/delete'):
        await delete_file(event)
    else:
        await event.reply("Не распознана команда, напишите /start для помощи")

bot.run_until_disconnected()
