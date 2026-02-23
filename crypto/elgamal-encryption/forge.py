#!/usr/bin/env python3
import requests
import base64
import json
import sys

TARGET = b'You got a 12 because you are an excellent student! :)'

def json_to_cookie(j: str) -> str:
    return base64.b64encode(j.encode(), altchars=b"-_").decode()

def get_params(server: str):
    r = requests.get(f"{server.rstrip('/')}/params/")
    r.raise_for_status()
    return r.json()

def encrypt_via_endpoint(server: str, data_hex: str):
    r = requests.get(f"{server.rstrip('/')}/encrypt_random_document_for_students/{data_hex}/")
    r.raise_for_status()
    return r.json()

def forge(orig_msg_hex: str, orig_ciphertext_hex: str, p: int) -> str:
    m_orig = int.from_bytes(bytes.fromhex(orig_msg_hex), 'big')
    m_target = int.from_bytes(TARGET, 'big')

    c_bytes = bytes.fromhex(orig_ciphertext_hex) # c1 = pow(g, y, p) || c2 = m * pow(h, y, p) % p
    length = len(c_bytes)//2
    c1 = int.from_bytes(c_bytes[:length], 'big')
    c2 = int.from_bytes(c_bytes[length:], 'big')

    k = (m_target * pow(m_orig, -1, p)) % p
    new_c2 = (c2 * k) % p

    new_c1_b = c1.to_bytes(length, 'big')
    new_c2_b = new_c2.to_bytes(length, 'big')
    new_ciphertext_hex = (new_c1_b + new_c2_b).hex()

    j = json.dumps({'msg': TARGET.hex(), 'ciphertext': new_ciphertext_hex})
    return json_to_cookie(j)

def main():
    server = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5001'
    params = get_params(server)
    p = int(params['p'])

    orig = b'hello'
    orig_hex = orig.hex()
    res = encrypt_via_endpoint(server, orig_hex)
    if 'error' in res:
        print('Endpoint error:', res['error'])
        return
    cookie = forge(res['msg'], res['ciphertext'], p)
    print(cookie)

if __name__ == '__main__':
    main()
