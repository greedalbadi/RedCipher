from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from os import urandom
from binascii import hexlify, unhexlify
from base64 import b64encode, b64decode
from src.handle_json import Handle_json
import hashlib
import os

class AES_encryptor:

    def __init__(self):

        self.key_length = 32 # 256 bits key length
        self.iv_length = 16 # 128 bits IV length

        self.h_obj = Handle_json()
        self.h_obj.load_json()

        # get the encrypted extention from the json file !
        self.ext = self.h_obj.get_ext()

        self.iv = urandom(self.iv_length)



    # Simple function for generating random 256 bit key and encode it
    def generate_key(self, enc="base64"):

        if enc.lower() == "base64":

            return b64encode( urandom(self.key_length) )

        elif enc.lower() == "hex":

            return hexlify( urandom(self.key_length) )

        else: return urandom(self.key_length)


    # this function convert plaintext to SHA-256 hashed text ( 32 bytes )
    def password_to_aes_key(self, password):

        if self.h_obj.settings["settings"]["use_salt"] == True:

            return hashlib.sha256(self.salt_password(password).encode()).digest()

        else:
            return hashlib.sha256(password.encode()).digest()

    
    # simple function for salting passwords !
    def salt_password(self, password):

        salt = self.h_obj.get_salt()

        mid_salt = len(salt) // 2

        # check if length of salt is even !
        if (len(salt) % 2) == 0:

            return salt[:mid_salt] + password + salt[mid_salt:]

        else:

            return password + salt




    # simple function to shred data and delete it 4Ever !
    def shreding_data(self, path, passes=3):
        

        # reading file and encrypt it with random 256 bit key
        with open(path, "rb+") as file:

            data = file.read()

            length = file.tell()

            encrypted_data = self.random_encryption(data)

            file.write(encrypted_data)

        file.close()
    

        # open the file and overwrite encrypted data with random data
        with open(path, "br+") as delfile:

            for _ in range(passes):

                delfile.seek(0)
                delfile.write(os.urandom(length))

            delfile.seek(0)
            delfile.write(b"\0" * length)

        os.remove(path)
        



    # encrypting data with random key and iv to make sure no one can restore it
    def random_encryption(self, data):

        key = self.generate_key("bytes")
        iv = urandom(16)

        cipher = AES.new(key, AES.MODE_CBC, iv)

        return cipher.encrypt(pad(data, AES.block_size))

    


    # Encrypt function with AES-256 CBC mode !
    def encrypt(self, data, key):

        cipher = AES.new(key, AES.MODE_CBC, self.iv)

        encrypted_data = cipher.encrypt(pad(data, AES.block_size))

        return self.iv + encrypted_data


    # Decrypt function with AES-256 CBC mode !
    def decrypt(self, enc_data, key):

        iv = enc_data[:16]

        cipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_data = cipher.decrypt(enc_data[16:])

        return unpad(decrypted_data, AES.block_size)


    # Encrypt file with AES-256 CBC mode 
    def encrypt_file(self, filename, key):

        enc_filename = self.ED_filename(filename, key)

        with open(filename, "rb") as file:

            data = file.read()


        file.close()

        if enc_filename != False:

            with open(enc_filename, "wb") as enc_file:

                encrypted_data = self.encrypt(data, key)

                enc_file.write(encrypted_data)


            enc_file.close()

        else:

            with open(filename + self.ext, "wb") as enc_file:

                encrypted_data = self.encrypt(data, key)

                enc_file.write(encrypted_data)


            enc_file.close()


        self.shreding_data(filename)


    # Decrypt file with AES-256 CBC mode !
    def decrypt_file(self, enc_filename, key):

        dec_filename = self.ED_filename(enc_filename, key, False)


        
        with open(enc_filename, "rb") as enc_file:

            enc_data = enc_file.read()

        enc_file.close()

        if dec_filename != False:

            with open(dec_filename, "wb") as dec_file:

                decrypted_data = self.decrypt(enc_data, key)

                dec_file.write(decrypted_data)


            dec_file.close()

        else:

            # split path to get filename !
            filename = os.path.splitext(enc_filename)

            with open(filename[0], "wb") as dec_file:

                decrypted_data = self.decrypt(enc_data, key)

                dec_file.write(decrypted_data)

            dec_file.close()

        self.shreding_data(enc_filename)


    # simple function take a path extract filename
    # and return it encrypted / decrypted !
    def ED_filename(self, filepath, key, encryption=True):

        dirname = os.path.dirname(filepath)
        basename = os.path.basename(filepath)

        if self.h_obj.settings["settings"]["encrypt_filename"] == True:

            if encryption:

                return dirname + "/" + hexlify(self.encrypt(basename.encode(), key)).decode() + self.ext

            elif not encryption:

                return dirname + "/" + self.decrypt(unhexlify(basename.replace(self.ext, "").encode()), key).decode()

        else: return False



# This function for test the Encryption !
def encrypt_test():

    key = b"Dd64YNior22mKIn/IBGb/pOSwrmTv1+K2yVojxNh1I4="

    print("Key: " + key.decode() + "\n")

    a_obj = AES_encryptor( b64decode(key) )

    msg = b"Hello Friend !"

    enc_msg = a_obj.encrypt(msg)

    print("Orignal: " + msg.decode() + "\n")
    print("Encrypt: " + b64encode(enc_msg).decode())


# This function for test Decryption !
def decrypt_test():

    key = b"Dd64YNior22mKIn/IBGb/pOSwrmTv1+K2yVojxNh1I4="

    a_obj = AES_encryptor( b64decode(key) )

    print("Key: " + key.decode() + "\n")
    
    enc_msg = b"MIP030NlsFwsOmbZfgwS92itmW9CVyaiQicQkwbEG3M="

    dec_msg = a_obj.decrypt( b64decode(enc_msg) )

    print("Encrypted: " + enc_msg.decode() + "\n")
    print("Decrypted: " + dec_msg.decode())



    


if __name__ == '__main__':

    while True:

        inp = input("(E) - Encrypt\n(D) - Decrypt\n(X) - Exit\n\n")

        if inp.upper() == "E":

            encrypt_test(); break

        elif inp.upper() == "D":

            decrypt_test(); break

        elif inp.upper() == "X":

            exit(1); break

        else: continue




    
