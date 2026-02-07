import nextcord, os, json
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
from nextcord.ui import View, Select, Button
from server import keep_alive

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

SUPPORT_LINK = "https://discord.gg/BCybjuZYH7"
IMG_BOT = "https://i.pinimg.com/originals/f2/51/97/f25197c789b8ad2de1d03a03ca14111d.gif"
DATA_FILE = "data.json"
DES_BOT = "แจกโค้ดบอทฟรี"

@bot.event
async def on_ready():
    print(f"บอทแจกไฟล์ [/คำสั่ง] | {bot.user}")

def load_google_credentials():
    creds = os.getenv("GOOGLE_CREDENTIALS")
    if not creds:
        raise Exception("ไม่พบ GOOGLE_CREDENTIALS ใน ENV")
    with open("credentials.json", "w", encoding="utf-8") as f:
        f.write(creds)

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=4)
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_data_from_backup():
    backup = connect_backup()
    records = backup.get_all_records()
    data = {}
    for row in records:
        data[row["name"]] = {
            "description": row["description"],
            "note": row["note"],
            "image": row["image"],
            "download": row["download"]
        }
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

load_google_credentials()
files_data = load_data_from_backup()
save_data(files_data)

# -- Dropdown --
class FileSelect(Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label=name,
                emoji="📁"
            )
            for name in files_data.keys()
        ]
        super().__init__(
            placeholder="⌜ เลือกรายการไฟล์ที่ต้องการที่นี่ ⌟",
            options=options
        )

    async def callback(self, interaction: Interaction):
        file_name = self.values[0]
        data = files_data[file_name]
        embed = nextcord.Embed(
            title="ข้อมูลไฟล์",
            color=0x2f3136
        )
        embed.add_field(
            name=f"📁 {file_name}",
            value=f"รายละเอียด:\n> {data['description']}\n\nหมายเหตุ:\n```{data['note']}```",
            inline=False
        )
        embed.set_image(url=data["image"])
        view = View()
        view.add_item(
            Button(
                label="𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝",
                style=nextcord.ButtonStyle.link,
                url=data["download"]
            )
        )

        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )

# -- Modal Add --
class AddFileModal(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(title="เพิ่มไฟล์ใหม่")
        self.name = nextcord.ui.TextInput(label="ชื่อไฟล์", required=True)
        self.description = nextcord.ui.TextInput(
            label="รายละเอียด",
            style=nextcord.TextInputStyle.paragraph,
            required=True
        )
        self.note = nextcord.ui.TextInput(
            label="หมายเหตุ",
            style=nextcord.TextInputStyle.paragraph,
            required=True
        )
        self.image = nextcord.ui.TextInput(label="ลิงก์รูปภาพ", required=True)
        self.download = nextcord.ui.TextInput(label="ลิงก์ดาวน์โหลด", required=True)
        for item in [self.name, self.description, self.note, self.image, self.download]:
            self.add_item(item)
    async def callback(self, interaction: nextcord.Interaction):
        files_data[self.name.value] = {
            "description": self.description.value,
            "note": self.note.value,
            "image": self.image.value,
            "download": self.download.value
        }
        save_data(files_data)
        await interaction.response.send_message(
            f"✅ เพิ่มไฟล์ **{self.name.value}** และบันทึกลง data.json แล้ว",
            ephemeral=True
        )

# -- View หลัก --
class FreeView(View):
    def __init__(self):
        super().__init__(timeout=None)
        if files_data:  # มีไฟล์อย่างน้อย 1
            self.add_item(FileSelect())
        else:
            self.add_item(
                Button(
                    label="ยังไม่มีไฟล์ในระบบ",
                    style=nextcord.ButtonStyle.gray,
                    disabled=True
                )
            )
        self.add_item(
            Button(
                label=f"⌜ คลังข้อมูล: {len(files_data)} ไฟล์ ⌟",
                style=nextcord.ButtonStyle.gray,
                disabled=True
            )
        )
        self.add_item(
            Button(
                label="𝐒𝐔𝐏𝐏𝐎𝐑𝐓",
                style=nextcord.ButtonStyle.link,
                url=SUPPORT_LINK
            )
        )

# -- /freeforyou --
@bot.slash_command(name="freeforyou", description="แจกไฟล์ฟรี")
async def freeforyou(interaction: Interaction):
    embed = nextcord.Embed(
        title="🎁 FREE FOR YOU",
        description=DES_BOT,
        color=0x2bff00
    )
    embed.set_image(IMG_BOT)
    await interaction.response.send_message(
        embed=embed,
        view=FreeView()
    )

# -- /del --
@bot.slash_command(name="del", description="ลบไฟล์")
async def delete(interaction: nextcord.Interaction, name: str):
    if name not in files_data:
        await interaction.response.send_message("❌ ไม่พบไฟล์นี้", ephemeral=True)
        return
    del files_data[name]
    save_data(files_data)
    await interaction.response.send_message(
        f"🗑️ ลบไฟล์ **{name}** แล้ว",
        ephemeral=True
    )

# -- /add --
@bot.slash_command(name="add", description="เพิ่มไฟล์")
async def add(
    interaction: nextcord.Interaction,
    name: str,
    description: str,
    note: str,
    download: str,
    message_link: str,
    image: str = None
):
    image_url = image if image else IMG_BOT
    files_data[name] = {
        "description": description,
        "note": note,
        "image": image_url,
        "download": download
    }
    save_data(files_data)
    # แก้ไขข้อความจาก message link
    try:
        parts = message_link.split("/")
        guild_id = int(parts[-3])
        channel_id = int(parts[-2])
        message_id = int(parts[-1])
        guild = bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        embed = nextcord.Embed(
            title="🎁 FREE FOR YOU",
            description=DES_BOT,
            color=0x5865f2
        )
        embed.set_image(url=IMG_BOT)
        await message.edit(embed=embed, view=FreeView())
    except Exception as e:
        await interaction.response.send_message(
            f"⚠️ เพิ่มไฟล์แล้ว แต่แก้ไขข้อความไม่สำเร็จ\n```{e}```",
            ephemeral=True
        )
        return
    await interaction.response.send_message(
        f"✅ เพิ่มไฟล์ **{name}** และอัปเดทข้อความเรียบร้อย",
        ephemeral=True
    )

# -- RUN --
keep_alive()
bot.run(os.getenv("TOKEN_BOT"))





