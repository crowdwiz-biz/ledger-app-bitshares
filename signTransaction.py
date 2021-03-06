#!/usr/bin/env python3
"""
/*******************************************************************************
*  Copyright of the Contributing Authors; see CONTRIBUTORS.md.
*
*  Licensed under the Apache License, Version 2.0 (the "License");
*  you may not use this file except in compliance with the License.
*  You may obtain a copy of the License at
*
*      http://www.apache.org/licenses/LICENSE-2.0
*
*  Unless required by applicable law or agreed to in writing, software
*  distributed under the License is distributed on an "AS IS" BASIS,
*  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
*  See the License for the specific language governing permissions and
*  limitations under the License.
********************************************************************************/
"""

import binascii
import json
import struct
from asn1 import Encoder, Numbers
from bitsharesbase.signedtransactions import Signed_Transaction
from ledgerblue.comm import getDongle
import argparse
from bitshares import BitShares
from datetime import datetime, timedelta

def parse_bip32_path(path):
    if len(path) == 0:
        return bytes([])
    result = bytes([])
    elements = path.split('/')
    for pathElement in elements:
        element = pathElement.split('\'')
        if len(element) == 1:
            result = result + struct.pack(">I", int(element[0]))
        else:
            result = result + struct.pack(">I", 0x80000000 | int(element[0]))
    return result

def encode(chain_id, tx):
    encoder = Encoder()

    encoder.start()

    encoder.write(struct.pack(str(len(chain_id)) + 's', chain_id), Numbers.OctetString)
    encoder.write(bytes(tx['ref_block_num']), Numbers.OctetString)
    encoder.write(bytes(tx['ref_block_prefix']), Numbers.OctetString)
    encoder.write(bytes(tx['expiration']), Numbers.OctetString)
    encoder.write(bytes(tx['operations'].length), Numbers.OctetString)
    for opIdx in range(0, len(tx.toJson()['operations'])):
        encoder.write(bytes([tx['operations'].data[opIdx].opId]), Numbers.OctetString)
        encoder.write(bytes(tx['operations'].data[opIdx].op), Numbers.OctetString)

    if 'extension' in tx:
        encoder.write(bytes(tx['extension']), Numbers.OctetString)
    else:
        encoder.write(bytes([0]), Numbers.OctetString)

    return encoder.output()

parser = argparse.ArgumentParser()
parser.add_argument('--chain_id', help="use a custom Chain ID")
parser.add_argument('--path', help="SLIP-0048 path to use for signing")
parser.add_argument('--file', help="read transaction from JSON-formatted FILE")
parser.add_argument('--broadcast', help="broadcast transaction to network after signing", action='store_true')
parser.add_argument('--node', help="set node to be used for broadcast")
parser.add_argument('--tapos', help="get recent TaPOS block from network", action='store_true')
parser.add_argument('--expire', help="set the transaction expiration to [minutes] in the future")
args = parser.parse_args()

if args.path is None:
    args.path = "48'/1'/1'/0'/0'"

if args.file is None:
    args.file = 'example-tx/tx_transfer.json'

if args.node is None:
    args.node = 'wss://bitshares.openledger.info/ws'

donglePath = parse_bip32_path(args.path)
pathSize = int(len(donglePath) / 4)

with open(args.file) as f:
    obj = json.load(f)
    blockchain = BitShares(args.node)
    if args.tapos:
        txbuffer = blockchain.tx()
        obj['ref_block_num'] = txbuffer['ref_block_num']
        obj['ref_block_prefix'] = txbuffer['ref_block_prefix']
        if args.expire and int(args.expire) >= 1:
            expiration = datetime.strptime(txbuffer['expiration'], "%Y-%m-%dT%H:%M:%S") + timedelta(minutes=int(args.expire)-1, seconds=30)
            txbuffer['expiration'] = expiration.strftime("%Y-%m-%dT%H:%M:%S%Z")
        obj['expiration'] = txbuffer['expiration']
    tx = Signed_Transaction(
            ref_block_num=obj['ref_block_num'],
            ref_block_prefix=obj['ref_block_prefix'],
            expiration=obj['expiration'],
            operations=obj['operations'],
        )
    if args.chain_id is None:
        args.chain_id = blockchain.rpc.chain_params['chain_id']
    signData = encode(binascii.unhexlify(args.chain_id), tx)
    print (binascii.hexlify(signData).decode())

    dongle = getDongle(True)
    offset = 0
    first = True
    singSize = len(signData)
    while offset != singSize:
        if singSize - offset > 200:
            chunk = signData[offset: offset + 200]
        else:
            chunk = signData[offset:]

        if first:
            totalSize = len(donglePath) + 1 + len(chunk)
            apdu = binascii.unhexlify("B5040000" + "{:02x}".format(totalSize) + "{:02x}".format(pathSize)) + donglePath + chunk
            first = False
        else:
            totalSize = len(chunk)
            apdu = binascii.unhexlify("B5048000" + "{:02x}".format(totalSize)) + chunk

        offset += len(chunk)
        result = dongle.exchange(apdu)
        print (binascii.hexlify(result).decode())
    if args.broadcast:
        tx_sig = blockchain.new_tx(json.loads(str(tx)))
        tx_sig["signatures"].extend([binascii.hexlify(result).decode()])
        print (tx_sig)
        print (blockchain.broadcast(tx=tx_sig))
