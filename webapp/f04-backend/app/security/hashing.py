from passlib.context import CryptContext
from cryptography.fernet import Fernet
import os
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash():
    def bcrypt(password: str):
        return pwd_cxt.hash(password)

    def verify(hashed_password,plain_password):
        return pwd_cxt.verify(plain_password,hashed_password)

    def generate_key():
        """
        Generates a key and save it into a file
        """
        return Fernet.generate_key()

    def encrypt_message(message, key=os.getenv("HASH_KEY", 'yyYND3dC3yB0nqP-Zn3r_OtHWQIU1yKGktDgJEugg_g=')):
        """
        Encrypts a message
        """
        encoded_message = message.encode()
        f = Fernet(key)
        encrypted_message = f.encrypt(encoded_message)

        return encrypted_message.decode('utf-8')

    def decrypt_message(encrypted_message, key=os.getenv("HASH_KEY", 'yyYND3dC3yB0nqP-Zn3r_OtHWQIU1yKGktDgJEugg_g=')):
        """
        Decrypts an encrypted message
        """
        f = Fernet(key)
        decrypted_message = f.decrypt(encrypted_message.encode('utf-8'))

        return decrypted_message.decode('utf-8')