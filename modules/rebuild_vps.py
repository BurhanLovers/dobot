import digitalocean
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.db import AccountsDB

# Fungsi untuk melakukan rebuild VPS
def rebuild_vps(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]  # Mendapatkan ID dokumen akun dari data
    droplet_id = data['droplet_id'][0]  # Mendapatkan ID VPS dari data

    # Mendapatkan informasi akun dari database berdasarkan ID
    account = AccountsDB().get(doc_id=doc_id)

    # Mengatur koneksi ke DigitalOcean menggunakan token akun
    manager = digitalocean.Manager(token=account['token'])

    # Mendapatkan informasi VPS berdasarkan ID
    droplet = manager.get_droplet(droplet_id)

    # Meminta konfirmasi dari pengguna sebelum melakukan rebuild
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Rebuild VPS", callback_data=f"confirm_rebuild?doc_id={doc_id}&droplet_id={droplet_id}"))
    keyboard.add(InlineKeyboardButton("Batalkan", callback_data="cancel_rebuild"))

    bot.send_message(
        chat_id=call.from_user.id,
        text=f"Apakah Anda yakin ingin me-rebuild VPS {droplet.name}?",
        reply_markup=keyboard
    )

# Fungsi untuk konfirmasi dan melanjutkan proses rebuild
def confirm_rebuild(call: CallbackQuery, data: dict):
    doc_id = data['doc_id'][0]
    droplet_id = data['droplet_id'][0]

    account = AccountsDB().get(doc_id=doc_id)
    manager = digitalocean.Manager(token=account['token'])
    droplet = manager.get_droplet(droplet_id)

    # Memulai proses rebuild
    droplet.rebuild()

    bot.send_message(
        chat_id=call.from_user.id,
        text=f"Rebuild VPS {droplet.name} telah dimulai."
    )

    # Menunggu hingga proses rebuild selesai
    action = droplet.get_actions()[0]  # Mendapatkan aksi terbaru
    action.wait()

    # Memuat kembali informasi droplet setelah rebuild
    droplet.load()

    # Mengirim pesan dengan informasi nama, IP, dan kata sandi droplet
    message = (
        f"Rebuild VPS {droplet.name} berhasil.\n\n"
        f"Nama: {droplet.name}\n"
        f"IP: {droplet.ip_address}\n"
        f"Kata Sandi: {password}"  # Pastikan Anda telah mendapatkan kata sandi dari tempat yang sesuai
    )
    bot.send_message(chat_id=call.from_user.id, text=message)

# Fungsi untuk membatalkan proses rebuild
def cancel_rebuild(call: CallbackQuery):
    bot.send_message(
        chat_id=call.from_user.id,
        text="Proses rebuild VPS dibatalkan."
    )
