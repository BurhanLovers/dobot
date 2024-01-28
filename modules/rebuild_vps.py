import digitalocean
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import AccountsDB
from _bot import bot

# Fungsi untuk melakukan rebuild VPS dengan pilihan Ubuntu atau Debian
def rebuild_vps(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]  # Mendapatkan ID dokumen akun dari data
    droplet_id = data['droplet_id'][0]  # Mendapatkan ID VPS dari data

    # Mendapatkan informasi akun dari database berdasarkan ID
    account = AccountsDB().get(doc_id=doc_id)

    # Mengatur koneksi ke DigitalOcean menggunakan token akun
    manager = digitalocean.Manager(token=account['token'])

    # Mendapatkan informasi VPS berdasarkan ID
    droplet = manager.get_droplet(droplet_id)

    # Membuat keyboard inline dengan pilihan Ubuntu atau Debian
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton("Ubuntu", callback_data=f"confirm_rebuild_os?doc_id={doc_id}&droplet_id={droplet_id}&image=ubuntu"),
        InlineKeyboardButton("Debian", callback_data=f"confirm_rebuild_os?doc_id={doc_id}&droplet_id={droplet_id}&image=debian")
    )
    keyboard.add(InlineKeyboardButton("Batalkan", callback_data="cancel_rebuild"))

    bot.send_message(
        chat_id=call.from_user.id,
        text=f"Pilih sistem operasi untuk me-rebuild VPS {droplet.name}:",
        reply_markup=keyboard
    )

# Fungsi untuk konfirmasi dan melanjutkan proses rebuild dengan sistem operasi yang dipilih
def confirm_rebuild(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]
    droplet_id = data['droplet_id'][0]
    chosen_image = data['image'][0]  # Mendapatkan pilihan sistem operasi dari data

    # Mendapatkan informasi akun dari database berdasarkan ID
    account = AccountsDB().get(doc_id=doc_id)

    # Mengatur koneksi ke DigitalOcean menggunakan token akun
    manager = digitalocean.Manager(token=account['token'])

    # Mendapatkan informasi VPS berdasarkan ID
    droplet = manager.get_droplet(droplet_id)

    # Menentukan ID sistem operasi berdasarkan pilihan
    image_id = "ubuntu-20-04-x64" if chosen_image == "ubuntu" else "debian-10-x64"

    # Memulai proses rebuild dengan sistem operasi yang dipilih
    droplet.rebuild(image=image_id)

    bot.send_message(
        chat_id=call.from_user.id,
        text=f"Rebuild VPS {droplet.name} dengan sistem operasi {chosen_image.capitalize()} telah dimulai."
    )

    # Menunggu hingga proses rebuild selesai
    action = droplet.get_actions()[0]  # Mendapatkan aksi terbaru
    action.wait()

    # Memuat kembali informasi droplet setelah rebuild
    droplet.load()

    # Mengirim pesan dengan informasi nama, IP, dan kata sandi droplet setelah rebuild
    message = (
        f"Rebuild VPS {droplet.name} dengan sistem operasi {chosen_image.capitalize()} berhasil.\n\n"
        f"Nama: {droplet.name}\n"
        f"IP: {droplet.ip_address}\n"
        f"Kata Sandi: {password}"  # Pastikan Anda telah mendapatkan kata sandi dari tempat yang sesuai
    )
    bot.send_message(chat_id=call.from_user.id, text=message)

