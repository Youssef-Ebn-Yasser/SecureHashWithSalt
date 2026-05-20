import secrets

import pandas as pd
import os
import random
import string

class HashAlgorithm:

    def __init__(self):
        self.initial_state = [
            0x6A09E667,
            0xBB67AE85,
            0x3C6EF372,
            0xA54FF53A,
            0x510E527F,
            0x9B05688C,
            0x1F83D9AB,
            0x5BE0CD19
        ]

    # -----------------------------------------------------
    # SALT GENERATOR with 16 character
    # -----------------------------------------------------
    def generate_salt(self):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(16))

    # -----------------------------------------------------
    # ROTATE RIGHT
    # -----------------------------------------------------
    def rotate_right(self, value, shift):
        return ((value >> shift) | (value << (32 - shift))) & 0xFFFFFFFF

    # -----------------------------------------------------
    # STRING TO BITS
    # -----------------------------------------------------
    def string_to_bits(self, text):
        bits = ""
        for char in text:
            ascii_value = ord(char)
            for i in range(7, -1, -1):
                bits += str((ascii_value >> i) & 1)
        return bits

    # -----------------------------------------------------
    # PADDING
    # -----------------------------------------------------
    def pad_message(self, bits):
        original_length = len(bits)

        bits += "1"

        while (len(bits) % 512) != 448:
            bits += "0"

        length_bits = bin(original_length)[2:].zfill(64)
        bits += length_bits

        return bits

    # -----------------------------------------------------
    # BLOCKS
    # -----------------------------------------------------
    def create_blocks(self, bits):
        return [bits[i:i+512] for i in range(0, len(bits), 512)]

    # -----------------------------------------------------
    # WORDS
    # -----------------------------------------------------
    def create_words(self, block):
        words = []
        for i in range(0, 512, 32):
            piece = block[i:i+32]
            number = 0
            for bit in piece:
                number = (number << 1) | int(bit)
            words.append(number)
        return words

    # -----------------------------------------------------
    # EXPAND WORDS
    # -----------------------------------------------------
    def expand_words(self, words):
        for i in range(16, 64):

            s0 = (
                self.rotate_right(words[i - 15], 7) ^
                self.rotate_right(words[i - 15], 18) ^
                (words[i - 15] >> 3)
            )

            s1 = (
                self.rotate_right(words[i - 2], 17) ^
                self.rotate_right(words[i - 2], 19) ^
                (words[i - 2] >> 10)
            )

            words.append(
                (words[i - 16] + s0 + words[i - 7] + s1) & 0xFFFFFFFF
            )

        return words

    # -----------------------------------------------------
    # COMPRESS
    # -----------------------------------------------------
    def compress(self, words):

        a, b, c, d, e, f, g, h = self.initial_state

        constants = [
            0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
            0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5
        ]

        for i in range(64):

            k = constants[i % len(constants)]

            s1 = (
                self.rotate_right(e, 6) ^
                self.rotate_right(e, 11) ^
                self.rotate_right(e, 25)
            )

            ch = (e & f) ^ ((~e) & g)

            temp1 = (h + s1 + ch + k + words[i]) & 0xFFFFFFFF

            s0 = (
                self.rotate_right(a, 2) ^
                self.rotate_right(a, 13) ^
                self.rotate_right(a, 22)
            )

            maj = (a & b) ^ (a & c) ^ (b & c)

            temp2 = (s0 + maj) & 0xFFFFFFFF

            h = g
            g = f
            f = e
            e = (d + temp1) & 0xFFFFFFFF
            d = c
            c = b
            b = a
            a = (temp1 + temp2) & 0xFFFFFFFF

        for i, val in enumerate([a, b, c, d, e, f, g, h]):
            self.initial_state[i] = (self.initial_state[i] + val) & 0xFFFFFFFF

    # -----------------------------------------------------
    # FINAL HASH
    # -----------------------------------------------------
    def final_hash(self):
        return ''.join(hex(v)[2:].zfill(8) for v in self.initial_state)

    # -----------------------------------------------------
    # HASH (salt$hash)
    # -----------------------------------------------------
    def hash(self, text, salt=None):

        self.__init__()

        if salt is None:
            salt = self.generate_salt()

        text = text + salt

        bits = self.string_to_bits(text)
        bits = self.pad_message(bits)

        for block in self.create_blocks(bits):
            words = self.create_words(block)
            words = self.expand_words(words)
            self.compress(words)

        return salt + "$" + self.final_hash()

    # -----------------------------------------------------
    # VERIFY
    # -----------------------------------------------------
    def verify(self, password, stored_value):

        salt, real_hash = stored_value.split("$")

        new_value = self.hash(password, salt)

        _, computed_hash = new_value.split("$")

        result = secrets.compare_digest(computed_hash, real_hash)
        return result