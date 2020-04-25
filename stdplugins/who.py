# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import asyncio
import html
import logging
import textwrap

from telethon import events, utils
from telethon.errors import MessageTooLongError
from telethon.tl import types

from sample_config import Config

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)
logger = logging.getLogger(__name__)




def get_who_string(who):
    who_string = html.escape(utils.get_display_name(who))
    if isinstance(who, (types.User, types.Channel)) and who.username:
        who_string += f" <i>(@{who.username})</i>"
    who_string += f", <a href='tg://user?id={who.id}'>#{who.id}</a>"
    return who_string


@borg.on(events.NewMessage(pattern=r"\.who", outgoing=True))  
async def _(event):
    if not event.message.is_reply:
        who = await event.get_chat()
    else:
        msg = await event.message.get_reply_message()
        if msg.forward:
          	# FIXME forward privacy memes
            who = await borg.get_entity(
                msg.forward.from_id or msg.forward.channel_id)
        else:
            who = await msg.get_sender()

    await event.edit(get_who_string(who), parse_mode='html')


@borg.on(events.NewMessage(pattern=r"\.members", outgoing=True))  
async def _(event):
    members = []
    async for member in borg.iter_participants(event.chat_id):
        if not member.deleted:
            messages = await borg.get_messages(
                event.chat_id,
                from_user=member,
                limit=0
            )
        members.append((
            messages.total,
            f"{messages.total} - {get_who_string(member)}"
        ))
    members = (
        m[1] for m in sorted(members, key=lambda m: m[0], reverse=True)
    )
    try:
        await event.edit("\n".join(members), parse_mode='html')
    except MessageTooLongError:
        res = textwrap.wrap(res, 4096-len(members))
        for part in res[1::]:
            await asyncio.sleep(1)
            await event.reply(f"<code>{part}</code>")
