import asyncio
import logging
from pyrogram import Client, idle, filters, emoji
from pyrogram.types import Message, Poll
from pyrogram.enums.chat_type import ChatType
from pyrogram.errors.exceptions import MessageNotModified, RevoteNotAllowed

# import configuration data
from USER_DATA import API_ID, API_HASH, EXPLANATION_TEXT, DEFAULT_CHECK

api_id = API_ID
api_hash = API_HASH


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    main_filter = filters.user(
        users=["me"]) & filters.text  # & ~filters.edited

    app = Client("my_account", api_id, api_hash)

    # @app.on_message(filters.text & filters.private)
    # async def echo(client, message):
    #     await message.reply(message.text)

    @app.on_message()
    async def ra(_, msg):
        print("Ra oooh")
        await app.send_message("me", "aye aye radi!")
        await msg.edit_text(" msg")

    #-------Get members-----------#
    # Get members
    # @app.on_message()
    # async def get_members(_, msg:Message):
        # check
        print(msg.chat.type)
        if not msg.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP, ChatType.CHANNEL]:
            print("not group")
            return
        count = await app.get_chat_members_count(msg.chat.id)
        print(count)
        print(msg)
        async for member in app.get_chat_members(msg.chat.id):
            print(member)

        # # Get administrators
        # administrators = []
        # async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        #     administrators.append(m)

        # # Get bots
        # bots = []
        # async for m in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.BOTS):
        #     bots.append(m)

    #------Add members-----------#
        # async def add_members(_, msg:Message):
        #     # Add multiple members to a group or channel
        #     await app.add_chat_members(chat_id, [user_id1, user_id2, user_id3])

    await app.start()
    logging.info("userbot started")
    await idle()
    logging.info("userbot stopped")
    await app.stop()


asyncio.run(main())
