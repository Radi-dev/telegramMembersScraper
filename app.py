import asyncio
import json
import logging
import os
import re
import time
import random
from pyrogram import Client, idle, filters, emoji
from pyrogram.types import Message, Poll, Chat, ChatMember
from pyrogram.enums.chat_type import ChatType
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions import MessageNotModified, RevoteNotAllowed

# import configuration data
from USER_DATA import API_ID, API_HASH, EXPLANATION_TEXT, DEFAULT_CHECK

api_id = API_ID
api_hash = API_HASH

cfg = {
    "include_bots": False,
    "include_admins": True,
    "include_deleted": False
}


async def extract_group_info(m: Message):
    """
    return
    """
    text = m.text or m.caption
    # "^!add(\n(([a-zA-Z0-9_]{5,32})|([\-]?[0-9]){5,15})){2}$"
    group_add_pattern = "^(([\-]?[0-9]){5,15}(\n))(([\-]?[0-9]){5,15})$"
    if match := re.match(group_add_pattern, text):
        log += "\npattern matched"
        await m.edit_text(log)
        entry = match.group()
        # r"([a-zA-Z0-9_]{5,32}|[-]?[0-9]{5,15})"
        group_name_pattern = r"[-]?[0-9]{5,15}"
        return re.findall(group_name_pattern, text)
    logging.info("No names matched")


async def fetch_groups(c: Client, m: Message):
    group_info = await extract_group_info(m)
    logging.info("extracted: poll info: %s", group_info)
    if not group_info:
        logging.info("groups not found")
        return
    if not len(group_info) == 2:
        logging.info("invalid number of groups found")
        return
    a, b = group_info

    # try:
    #     target_group = await c.get_chat(-abs(int(b)))
    # except:
    #     target_group = await c.get_chat(int(b))
    # try:
    #     source_group = await c.get_chat(-abs(int(a)))
    # except:
    #     source_group = await c.get_chat(int(a))
    target_group = await c.get_chat(-abs(int(b)))
    source_group = await c.get_chat(-abs(int(a)))
    # f"group with name or id {b} not found"
    return source_group, target_group


async def get_members(c: Client, target_group: Chat):
    # print(msg)
    members = []
    #i = 1
    async for member in c.get_chat_members(int(target_group.id)):
        # if not cfg["include_admins"] and ChatMember.
        members.append(member)
        # if (i) % 100 == 0:
        #     wait_time = random.randint(5, 15)
        #     log = f"\nwaiting {wait_time} seconds to avoid banning\n"
        #     time.sleep(wait_time)
        #     logging.info(log)
        # i += 1
    return members

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
    return members


async def add_members_to_group(client: Client, chat_id: int, user_ids: list[int]):
    # Add multiple members to a group or channel
    print(chat_id, user_ids)
    for i in user_ids:
        try:
            await client.add_chat_members(chat_id, i)
        except Exception as err:
            print(err)

    # await client.add_chat_members(chat_id, user_ids)


async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    main_filter = filters.user(
        users=["me"]) & filters.text  # & ~filters.edited

    app = Client("my_account", api_id, api_hash)

    # @app.on_message(filters.text & filters.private)
    # async def echo(client, message):
    #     await message.reply(message.text)
    @app.on_message(filters.regex(r"[gG]et.$"))
    async def get_chat_members(c: Client, m: Message):
        """Get members and save to file"""
        print('Gettt')
        if m.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
            log = "`Checking ...`"
            await m.edit_text(log)
            try:
                source_group = await c.get_chat(-abs(m.chat.id))
                log += "\n`Found, fetching ...`"
                await m.edit_text(log)

            except:
                log += "`Group not found.`"
                await m.edit_text(log)
                time.sleep(2)
                return await m.delete()
            # members = await get_members(c, source_group)
            #member_ids = [i.user.id for i in members]
            # print(member_ids)
            #members_list = {'members': member_ids}

            with open('members.json', 'w') as f:
                json.dump({'members': []}, f)
            async for member in c.get_chat_members(source_group.id):
                # if not cfg["include_admins"] and ChatMember.
                with open('members.json', 'r+') as f:
                    print(f.read())
                    f.seek(0)
                    users = json.loads(f.read())
                    f.seek(0)
                    print('users is', users)
                    try:
                        members_list = users['members']
                    except:
                        continue
                    members_list.append(member.user.id)
                    users['members'] = members_list
                    json.dump(users, f)
                    f.truncate()
            log += "`Done.`"
            await m.edit_text(log)
            time.sleep(2)
            return await m.delete()

    @ app.on_message(filters.regex(r"[aA]dd.$"))
    async def add_members(c: Client, m: Message):
        print('addd')
        m_reply = m.reply_to_message
        # if not m_reply:
        #     await m.edit_text(
        #         "`!add`"
        #         "\n- invalid command, try again as a reply "
        #         "to another message which include names of "
        #         "source and target groups"
        #     )
        #     return
        if m_reply:
            log = "`!add`\n- fetching members"
            await m.edit_text(log)
            m_groups = await fetch_groups(c, m_reply)
            if not m_groups:
                log += "\n- groups not found"
                await m.edit_text(log)
                return
            source_group, target_group = m_groups
            members_count = await c.get_chat_members_count(source_group.id)
            log += f"\n- found {members_count} members"
            await m.edit_text(log)
            members = await get_members(c, source_group)
            # print("mmbrs", members)
            member_ids = [int(member.user.id) for member in members]
            log += f"\n- will add {len(members)} members"
            await m.edit_text(log)
            # await add_members_to_group(c, int(target_group.id), member_ids)

            # Add multiple members to a group or channel
            log += f"\n- Added count:\n"
            await m.edit_text(log)
            for i, _id in enumerate(member_ids):
                try:
                    await c.add_chat_members(int(target_group.id), _id)
                    log += f"{i+1}, "
                    await m.edit_text(log)
                except FloodWait as e:
                    log += f"\nwaiting {e.value} seconds to avoid banning\n"
                    await m.edit_text(log)
                    time.sleep(int(e.value))
                except Exception as err:
                    print(err)

            log += f"\n- Added members"
            await m.edit_text(log)
            time.sleep(2)
            return await m.delete()
            # except:
            #     logging.info("Adding failed")
        else:
            """Check if group,
            Read files and add the members"""
            if not os.path.exists('members.json'):
                return logging.info("members file not found")

            with open('members.json', 'r') as file:
                users = json.load(file)
                try:
                    members_list = users['members']
                except:
                    logging.info("Not accessed members")
                    return
            print('got list')
            if m.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                log = "`Checking ...`"
                await m.edit_text(log)
                try:
                    target_group = await c.get_chat(-abs(m.chat.id))
                    log += "\n`Found, fetching ...`"
                    await m.edit_text(log)

                except:
                    log += "`Group not found."
                    await m.edit_text(log)
                    time.sleep(2)
                    return await m.delete()
                existing_members = await get_members(c, target_group)
                existing_member_ids = [i.user.id for i in existing_members]
                try:
                    members_list = [
                        i for i in members_list if i not in existing_member_ids]
                except:
                    pass
                if os.path.exists('error_members.json'):
                    error_members = []
                    with open('error_members.json', 'r') as file:
                        users = json.load(file)
                        try:
                            error_members = users['error_members']
                        except:
                            logging.info("Not accessed error members")
                            return
                        try:
                            members_list = [
                                i for i in members_list if i not in error_members]
                        except:
                            pass

            if members_length := len(members_list):

                log += f"\n- will add {members_length}"
                await m.edit_text(log)
                # await add_members_to_group(c, int(target_group.id), member_ids)

                # Add multiple members to a group or channel
                log += f"\n- Added count:\n"
                await m.edit_text(log)
                for i, _id in enumerate(members_list):
                    try:
                        await c.add_chat_members(target_group.id, _id)
                        log += f"{i+1}, "
                        await m.edit_text(log)
                    except FloodWait as e:
                        log += f"\nwaiting {e.value} seconds to avoid banning\n"
                        await m.edit_text(log)
                        time.sleep(int(e.value))
                        # await asyncio.sleep(e.value)
                    except Exception as err:
                        logging.info(err)

                        if not os.path.exists('error_members.json'):
                            with open('error_members.json', 'w') as f:
                                json.dump({'error_members': []}, f)
                        with open('error_members.json', 'r+') as f:
                            f.seek(0)
                            error_users = json.loads(f.read())
                            f.seek(0)
                            try:
                                error_members_list = error_users['error_members']
                            except:
                                continue
                            error_members_list.append(_id)
                            error_users['error_members'] = error_members_list
                            json.dump(error_users, f)
                            f.truncate()

    await app.start()
    logging.info("userbot started")
    await idle()
    logging.info("userbot stopped")
    await app.stop()


asyncio.run(main())
