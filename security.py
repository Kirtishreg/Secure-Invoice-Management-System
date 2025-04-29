from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import os
import hashlib

from flask_mail import Mail, Message
from flask import current_app

KEY_SIZE = 32  # AES-256
BLOCK_SIZE = 16
mail = Mail()

def generate_key():
    return os.urandom(KEY_SIZE)

def encrypt_data(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data.encode(), BLOCK_SIZE))
    return cipher.iv + ct_bytes  # Prepend IV to ciphertext for decryption

def decrypt_data(encrypted_data, key):
    iv = encrypted_data[:BLOCK_SIZE]
    ct = encrypted_data[BLOCK_SIZE:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(ct), BLOCK_SIZE).decode()

def hash_data(data):
    return hashlib.sha256(data.encode()).hexdigest()


def send_email(to, subject, body):
    msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[to])
    msg.body = body
    mail.send(msg)