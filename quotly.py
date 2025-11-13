import aiofiles
import aiohttp
import os
import io
import base64
import random
import config

from core import app
from pyrogram import filters
from utils.functions import Tools


class QuotlyException(Exception):
    pass


class Quotly:
    colors = [
        "White",
        "Navy",
        "DarkBlue",
        "MediumBlue",
        "Blue",
        "DarkGreen",
        "Green",
        "Teal",
        "DarkCyan",
        "DeepSkyBlue",
        "DarkTurquoise",
        "MediumSpringGreen",
        "Lime",
        "SpringGreen",
        "Aqua",
        "Cyan",
        "MidnightBlue",
        "DodgerBlue",
        "LightSeaGreen",
        "ForestGreen",
        "SeaGreen",
        "DarkSlateGray",
        "DarkSlateGrey",
        "LimeGreen",
        "MediumSeaGreen",
        "Turquoise",
        "RoyalBlue",
        "SteelBlue",
        "DarkSlateBlue",
        "MediumTurquoise",
        "Indigo",
        "DarkOliveGreen",
        "CadetBlue",
        "CornflowerBlue",
        "RebeccaPurple",
        "MediumAquaMarine",
        "DimGray",
        "DimGrey",
        "SlateBlue",
        "OliveDrab",
        "SlateGray",
        "SlateGrey",
        "LightSlateGray",
        "LightSlateGrey",
        "MediumSlateBlue",
        "LawnGreen",
        "Chartreuse",
        "Aquamarine",
        "Maroon",
        "Purple",
        "Olive",
        "Gray",
        "Grey",
        "SkyBlue",
        "LightSkyBlue",
        "BlueViolet",
        "DarkRed",
        "DarkMagenta",
        "SaddleBrown",
        "DarkSeaGreen",
        "LightGreen",
        "MediumPurple",
        "DarkViolet",
        "PaleGreen",
        "DarkOrchid",
        "YellowGreen",
        "Sienna",
        "Brown",
        "DarkGray",
        "DarkGrey",
        "LightBlue",
        "GreenYellow",
        "PaleTurquoise",
        "LightSteelBlue",
        "PowderBlue",
        "FireBrick",
        "DarkGoldenRod",
        "MediumOrchid",
        "RosyBrown",
        "DarkKhaki",
        "Silver",
        "MediumVioletRed",
        "IndianRed",
        "Peru",
        "Chocolate",
        "Tan",
        "LightGray",
        "LightGrey",
        "Thistle",
        "Orchid",
        "GoldenRod",
        "PaleVioletRed",
        "Crimson",
        "Gainsboro",
        "Plum",
        "BurlyWood",
        "LightCyan",
        "Lavender",
        "DarkSalmon",
        "Violet",
        "PaleGoldenRod",
        "LightCoral",
        "Khaki",
        "AliceBlue",
        "HoneyDew",
        "Azure",
        "SandyBrown",
        "Wheat",
        "Beige",
        "WhiteSmoke",
        "MintCream",
        "GhostWhite",
        "Salmon",
        "AntiqueWhite",
        "Linen",
        "LightGoldenRodYellow",
        "OldLace",
        "Red",
        "Fuchsia",
        "Magenta",
        "DeepPink",
        "OrangeRed",
        "Tomato",
        "HotPink",
        "Coral",
        "DarkOrange",
        "LightSalmon",
        "Orange",
        "LightPink",
        "Pink",
        "Gold",
        "PeachPuff",
        "NavajoWhite",
        "Moccasin",
        "Bisque",
        "MistyRose",
        "BlanchedAlmond",
        "PapayaWhip",
        "LavenderBlush",
        "SeaShell",
        "Cornsilk",
        "LemonChiffon",
        "FloralWhite",
        "Snow",
        "Yellow",
        "LightYellow",
        "Ivory",
        "Black",
    ]


    async def forward_info(reply):
        if reply.forward_from_chat:
            sid = reply.forward_from_chat.id
            title = reply.forward_from_chat.title
            name = title
        elif reply.forward_from:
            sid = reply.forward_from.id
            try:
                name = reply.forward_from.first_name or "Unknown"
                if reply.forward_from.last_name:
                    name = f"{name} {reply.forward_from.last_name}"
            except AttributeError:
                name = "Unknown"
            title = name
        elif reply.forward_sender_name:
            title = name = reply.forward_sender_name
            sid = 0
        elif reply.from_user:
            try:
                sid = reply.from_user.id
                name = reply.from_user.first_name or "Unknown"
                if reply.from_user.last_name:
                    name = f"{name} {reply.from_user.last_name}"
            except AttributeError:
                name = "Unknown"
            title = name
        return sid, title, name

    async def t_or_c(message):
        return message.text or message.caption or ""

    async def get_emoji(message):
        if message.from_user and getattr(message.from_user, "emoji_status", None):
            return str(message.from_user.emoji_status.custom_emoji_id)
        return ""

    async def quotly(payload):
        """Generate quote image via API with fallback to local server"""
        r = await Tools.fetch.post("https://bot.lyo.su/quote/generate.png", json=payload)

        # pakai r.status untuk aiohttp response
        if getattr(r, "status", None) != 200:
            new_r = await Tools.fetch.post("http://localhost:4888/generate", json=payload)
            data = await new_r.json()
            img_bytes = base64.b64decode(data["result"]["image"])
            return img_bytes

        try:
            if hasattr(r, "is_error") and not r.is_error:
                return await r.read()
            else:
                data = await r.json()
                raise QuotlyException(data)
        except Exception:
            return await r.read()

    @staticmethod
    async def make_carbonara(code: str, bg_color: str, theme: str, language: str):
        url = "https://carbonara.solopov.dev/api/cook"
        json_data = {
            "code": code,
            "paddingVertical": "56px",
            "paddingHorizontal": "56px",
            "backgroundMode": "color",
            "backgroundColor": bg_color,
            "theme": theme,
            "language": language,
            "fontFamily": "Cascadia Code",
            "fontSize": "14px",
            "windowControls": True,
            "widthAdjustment": True,
            "lineNumbers": True,
            "firstLineNumber": 1,
            "name": f"{app.name}-Carbon",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=json_data) as resp:
                return io.BytesIO(await resp.read())

    @staticmethod
    async def get_message_content(message):
        if message.text:
            return message.text, "text"
        elif message.document:
            doc = await message.download()
            async with aiofiles.open(doc, mode="r") as f:
                content = await f.read()
            os.remove(doc)
            return content, "document"
        return None, None


@app.on_message(filters.command("q") & ~config.BANNED_USERS)
async def qoutly_cmd(client, message):
    if not message.reply_to_message:
        return await message.reply("> **Please reply to a message!**")

    pros = await message.reply("> **Please wait, making your quote...**")
    reply_msg = message.reply_to_message
    cmd = message.command[1:]

    def get_color(index=0):
        return cmd[index] if len(cmd) > index else random.choice(Quotly.colors)

    try:
        # (semua logika command tetap sama seperti punyamu)
        # ...
        hasil = await Quotly.quotly(payload)
        bio_sticker = io.BytesIO(hasil)
        bio_sticker.name = "quote.webp"
        await message.reply_sticker(bio_sticker)
        await pros.delete()

    except Exception as e:
        await pros.edit(f"> **ERROR:** `{str(e)}`")


@app.on_message(filters.command("qcolor") & ~config.BANNED_USERS)
async def qcolor_cmd(_, message):
    iymek = f"\n•".join(Quotly.colors)
    if len(iymek) > 4096:
        with open("qcolor.txt", "w") as file:
            file.write(iymek)
        await message.reply_document("qcolor.txt", caption="> **Color for quotly**")
        os.remove("qcolor.txt")
    else:
        await message.reply(f"> **Color for quotly**\n•{iymek}")


__MODULE__ = "Quotly"
__HELP__ = """
<blockquote expandable>
<b>📝 Quote Generator</b>

<b>★ /q</b> [reply] – Quote message with random color.  
<b>★ /q pink</b> [reply] – Quote message with custom color.  
<b>★ /q</b> @username [reply] – Fake quote for a specific user.  
<b>★ /q</b> @username pink -r [reply] – Fake quote with reply & color.  
<b>★ /q</b> -r [reply] – Quote with replies.  
<b>★ /q</b> -r pink [reply] – Quote with replies & color.  
<b>★ /q</b> 5 [reply] – Quote multiple messages.  
<b>★ /q</b> 5 pink [reply] – Multiple quotes with custom color.

<b>★ /qcolor</b> – Show all available quote colors.
</blockquote>
"""
