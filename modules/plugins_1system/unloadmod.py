from pyrogram import Client, filters
from modules.plugins_1system.settings.main_settings import module_list, file_list
from modules.plugins_1system.restarter import restart
from prefix import my_prefix

import os


@Client.on_message(filters.command('unloadmod', prefixes=my_prefix()) & filters.me)
async def unloadmod(client, message):
    try:
        module_name = message.text.replace(f'{my_prefix()}unloadmod', '')
        params = module_name.split()
        module_name = params[0]
        del module_list[module_name]
        file = file_list[module_name]
        os.remove(f'modules/plugins_2custom/{file}')
        await message.edit("**The module has been successfully unloaded.**\nRestart...")
        await restart(message, restart_type="restart")
    except Exception as error:
        await message.edit(f"**An error has occurred.**\nLog: not found {error}")


module_list['Unloadmod'] = f'{my_prefix()}unloadmod [module name]'
