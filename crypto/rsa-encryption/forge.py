#!/usr/bin/env python3
import requests
import base64
import json
import sys
import secrets
from Crypto.Util.number import getPrime, inverse, bytes_to_long

def pkcs1_pad(message, block_size):
    """Pads message using PKCS#1 v1.5 scheme."""
    if len(message) > block_size - 11:
        raise ValueError("Message too long for RSA block size")
    padding_length = block_size - len(message) - 3
    padding = secrets.token_bytes(padding_length).replace(b"\x00", b"\x01")  # Avoid null bytes
    return b"\x00\x02" + padding + b"\x00" + message

def get_params(server: str):
  r = requests.get(f"{server.rstrip("/")}/pk/")
  r.raise_for_status()
  return r.json()

def get_message(server:str):
  res = requests.get(f"{server.rstrip("/")}/")
  res.raise_for_status()
  return res.cookies.get("authtoken")

# code to set a auth token and send a request to the quote page
def test_quote(server:str):
    # get the public parameters
    pp = get_params(server)
    message = get_message(server)
    N = pp['N']
    e = pp['e']
    secret = get_secret(message, N, e)
    custom_plaintext = f'"{secret}" because of weird oracles!'.encode()
    custom_ciphertext = forge(custom_plaintext, N, e)
    cookies = {"authtoken": custom_ciphertext.hex()}

    res = requests.get(f"{server.rstrip("/")}/quote/", cookies=cookies)
    res.raise_for_status()
    return res.text

def forge(message: bytes, N, e) -> bytes:
    # modulus and private exponent

    """Encrypts message with PKCS#1 v1.5 padding."""
    block_size = (N.bit_length() + 7) // 8
    padded_message = pkcs1_pad(message, block_size)
    m = bytes_to_long(padded_message)
    # compute the ciphertext
    c = pow(m, e, N)
    # encode the ciphertext into a bytes using big-endian byte order
    ciphertext = c.to_bytes(block_size, 'big')
    return ciphertext

#TODO
def get_secret(message, N, e):
   return
   
# print(get_params("https://rsaenc.syssec.dk/"))

print(test_quote("https://rsaenc.syssec.dk/"))