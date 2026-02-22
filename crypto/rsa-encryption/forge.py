#!/usr/bin/env python3
import requests
import base64
import json
import sys
import secrets
import tqdm
from Crypto.Util.number import getPrime, inverse, bytes_to_long

def pkcs1_pad(message, block_size):
    """Pads message using PKCS#1 v1.5 scheme."""
    if len(message) > block_size - 11:
        raise ValueError("Message too long for RSA block size")
    padding_length = block_size - len(message) - 3
    padding = secrets.token_bytes(padding_length).replace(b"\x00", b"\x01")  # Avoid null bytes
    return b"\x00\x02" + padding + b"\x00" + message

def pkcs1_unpad(padded_message, block_size):
    if len(padded_message) != block_size:
        return None  # Invalid length

    if padded_message[0] != 0x00 or padded_message[1] != 0x02:
        return None  # Invalid padding format

    # Find the 0x00 separator (must be after padding)
    separator_index = padded_message.find(0x00, 2)
    if separator_index == -1:
        return None  # No separator found, invalid padding

    # Extract the actual message (everything after the 0x00 separator)
    return padded_message[separator_index + 1:]


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
    bypass = "Not using proper OAEP is dangerous ..." # add here the secret if known already
    if not bypass:
        secret = lsb_attack(message, N, e, server)
        print(f"Recovered secret: {secret}")
    else:
        secret = bypass

    custom_plaintext = f'{secret} because of weird oracles!'.encode()
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

def lsb_attack(ciphertext_hex: str, N, e, server: str):
    """Recover the original plaintext using a parity (LSB) oracle.

    The `/quote/` endpoint reveals whether the decrypted value is even or odd.
    We repeatedly double the ciphertext (multiplied by 2^e mod N) and use the
    parity responses to binary search the plaintext interval [low, high).
    """
    even = "I do not like even numbers."  

    block_size = (N.bit_length() + 7) // 8

    # start from the provided ciphertext c0
    current_c = bytes_to_long(bytes.fromhex(ciphertext_hex))
    two_pow_e = pow(2, e, N)

    low, high = 0, N

    def is_even(c_int: int) -> bool:
        """Query oracle with ciphertext int -> True if plaintext is even."""
        ct = c_int.to_bytes(block_size, "big")
        cookies = {"authtoken": ct.hex()}
        res = requests.get(f"{server.rstrip('/')}/quote/", cookies=cookies)
        res.raise_for_status()
        return res.text == even

    # https://crypto.stackexchange.com/questions/11053/rsa-least-significant-bit-oracle-attack
    total_iters = N.bit_length()  # binary search will need at most this many steps
    with tqdm.tqdm(total=total_iters, desc="LSB oracle", unit="iter") as pbar:
        while high - low > 1:
            current_c = (current_c * two_pow_e) % N
            mid = (low + high) // 2
            if is_even(current_c):
                high = mid
            else:
                low = mid

            # progress + quick sense of remaining search space
            pbar.update(1)
            remaining_bits = (high - low).bit_length()
            pbar.set_postfix_str(f"range≈2^{remaining_bits}")

    recovered = low.to_bytes(block_size, "big")
    recovered = pkcs1_unpad(recovered, block_size)
    secret = recovered[recovered.find(b'"') + 1 : recovered.rfind(b'"')].decode()
    print(f"Recovered plaintext: {recovered}")
    return secret




# print(get_params("https://rsaenc.syssec.dk/"))

print(test_quote("https://rsaenc.syssec.dk/"))
