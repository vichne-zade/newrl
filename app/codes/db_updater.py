import codecs
import math
from subprocess import call
import uuid
import ecdsa
from Crypto.Hash import keccak
import os
import json
import datetime
import time
import sqlite3
import hashlib

from app.codes.clock.global_time import get_corrected_time_ms
from app.nvalues import MIN_STAKE_AMOUNT
from ..Configuration import Configuration

from ..constants import INITIAL_NETWORK_TRUST_SCORE, NEWRL_DB
from .utils import get_person_id_for_wallet_address, get_time_ms
from ..ntypes import NEWRL_TOKEN_CODE
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
def __is_smart_contract(cur,address):
    if not address.startswith('ct'):
        return False

    sc_cursor = cur.execute(
        'SELECT COUNT (*) FROM contracts WHERE address=?', (address, ))
    sc_id = sc_cursor.fetchone()
    if sc_id is None:
        return False
    else:
        return True
def is_wallet_valid(cur, address):
    wallet_cursor = cur.execute(
        'SELECT wallet_public FROM wallets WHERE wallet_address=?', (address, ))
    wallet = wallet_cursor.fetchone()
    if wallet is None:
        return False
    return True


def transfer_tokens_and_update_balances(cur, sender, reciever, tokencode, amount):
    if sender == reciever:
        print('Sender and receiver cannot be the same')
        return False
    if sender == Configuration.config('ZERO_ADDRESS') :
        print('Sender can not be zero address')
        return False
    if reciever == Configuration.config('ZERO_ADDRESS'):
        sender_balance = get_wallet_token_balance(cur, sender, tokencode)
        sender_balance = sender_balance - amount
        update_wallet_token_balance(cur, sender, tokencode, sender_balance)
    else:
        sender_balance = get_wallet_token_balance(cur, sender, tokencode)
        reciever_balance = get_wallet_token_balance(cur, reciever, tokencode)
        sender_balance = sender_balance - amount
        reciever_balance = reciever_balance + amount
        update_wallet_token_balance(cur, sender, tokencode, sender_balance)
        update_wallet_token_balance(cur, reciever, tokencode, reciever_balance)



def update_wallet_token_balance(cur, wallet_address, token_code, balance):
    cur.execute(f'''INSERT OR REPLACE INTO balances
				(wallet_address, tokencode, balance)
				 VALUES (?, ?, ?)''', (wallet_address, token_code, balance))


def update_trust_score(cur, personid1, personid2, new_score, tstamp):
    cur.execute(f'''INSERT OR REPLACE INTO trust_scores
				(src_person_id, dest_person_id, score, last_time)
				 VALUES (?, ?, ?, ?)''', (personid1, personid2, new_score, tstamp))


def add_wallet_pid(cur, wallet):
    # checking if this is a linked wallet or new one; for linked, no new personid is created
    if isinstance(wallet, str):
        wallet = json.loads(wallet)
    linkedstatus = wallet['specific_data']['linked_wallet'] if 'linked_wallet' in wallet['specific_data'] else False
    if linkedstatus:
        pid_cursor = cur.execute('SELECT person_id FROM person_wallet WHERE wallet_id=?',
                                 (wallet['specific_data']['parentaddress'], )).fetchone()
        pid = pid_cursor[0]
        if not pid:
            print("No personid linked to the parentwallet.")
            return False
    else:  # not a linked wallet, so create a new pid and update person table
        pid = get_person_id_for_wallet_address(wallet['wallet_address'])
        query_params = (pid, get_time_ms())
        cur.execute(f'''INSERT OR IGNORE INTO person
                    (person_id, created_time)
                    VALUES (?, ?)''', query_params)

    # for both new and linked wallet, update the wallet table and person_wallet table
    kyc_doc_json = json.dumps(wallet['kyc_docs'])
    data_json = json.dumps(wallet['specific_data'])
    query_params = (wallet['wallet_address'],
                    wallet['wallet_public'],
                    wallet['custodian_wallet'],
                    kyc_doc_json,
                    wallet['ownertype'],
                    wallet['jurisd'],
                    data_json
                    )
    if not __is_smart_contract(cur,wallet['wallet_address']):
        cur.execute(f'''INSERT OR IGNORE INTO wallets
            (wallet_address, wallet_public, custodian_wallet, kyc_docs, owner_type, jurisdiction, specific_data)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', query_params)

    query_params = (pid, wallet['wallet_address'])
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                (person_id, wallet_id)
                VALUES (?, ?)''', query_params)


def add_token(cur, token, txcode=None):
    tcodenewflag = False
    existingflag = False
    if 'tokencode' in token:  # creating more of an existing token or tokencode provided by user
        if token['tokencode'] and token['tokencode'] != "0" and token['tokencode'] != "":
            tid = cur.execute(
                'SELECT tokencode FROM tokens WHERE tokencode=?', (token['tokencode'], )).fetchone()
            if tid:  # tokencode exists, more of an existing token is being added to the first_owner
                tid = tid[0]
                existingflag = True
            else:
                # if provided code does not exist, it is considered new token addition
                tid = str(token['tokencode'])
                existingflag = False
        else:   # mistakenly entered tokencode value as "" or "0" or 0
            tcodenewflag = True
            existingflag = False
    if 'tokencode' not in token or tcodenewflag:   # new tokencode needs to be created
        randcode = create_contract_address()
        hs = hashlib.blake2b(digest_size=20)
        hs.update(randcode.encode())
        tid = 'tk' + hs.hexdigest()
        existingflag = False

    if not existingflag:    # new token to be created
        tokendecimal = token['tokendecimal'] if 'tokendecimal' in token else 0
        tokendecimal = int(tokendecimal)
        token_attributes_json = json.dumps(token['tokenattributes']) if 'tokenattributes' in token else {}
        disallowed_json = json.dumps(token['disallowed']) if 'disallowed' in token else {}
        query_params = (
            tid,
            token['tokenname'],
            token['tokentype'],
            token['first_owner'],
            token['custodian'],
            token['legaldochash'],
            token['amount_created'],
            token['sc_flag'],
            disallowed_json,
            txcode,
            tokendecimal,
            token_attributes_json
        )
        cur.execute(f'''INSERT OR IGNORE INTO tokens
            (tokencode, tokenname, tokentype, first_owner, custodian, legaldochash, 
            amount_created, sc_flag, disallowed, parent_transaction_code, tokendecimal, token_attributes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', query_params)
        if token['amount_created']:
            update_wallet_token_balance(
                cur, token['first_owner'], tid, token['amount_created'])

    # now update balance for case of more of existing created
    else:
        if token['first_owner'] and token['amount_created']:
            added_balance = int(token['amount_created'] or 0)
            current_balance = get_wallet_token_balance(
                cur, token['first_owner'], tid)
            balance = int(current_balance or 0) + added_balance
            update_wallet_token_balance(
                cur, token['first_owner'], tid, balance)
            update_token_amount(cur, tid, token['amount_created'])

    return True


def get_kyc_doc_hash_json(kyc_docs, kyc_doc_hashes):
    doc_list = []
    for idx, doc in enumerate(kyc_docs):
        doc_list.append({
            'type': doc,
            'hash': kyc_doc_hashes[idx]
        })
    return json.dumps(doc_list)


def get_wallet_token_balance(cur, wallet_address, token_code):
    balance_cursor = cur.execute('SELECT balance FROM balances WHERE wallet_address = :address AND tokencode = :tokencode', {
        'address': wallet_address, 'tokencode': token_code})
    balance_row = balance_cursor.fetchone()
    balance = balance_row[0] if balance_row is not None else 0
    return balance


def add_tx_to_block(cur, block_index, transactions):
    for transaction_signature in transactions:
        transaction = transaction_signature['transaction']
        signatures = json.dumps(transaction_signature['signatures'])
        signatures = [] if signatures is None else signatures
        transaction_code = transaction['transaction_code'] if 'transaction_code' in transaction else transaction['trans_code']
        description = transaction['descr'] if 'descr' in transaction else transaction['description']
        specific_data = json.dumps(
            transaction['specific_data']) if 'specific_data' in transaction else ''
        db_transaction_data = (
            block_index,
            transaction_code,
        )
        cur.execute(f'''INSERT OR IGNORE INTO transactions
            (block_index, transaction_code)
            VALUES (?, ?)''', db_transaction_data)


def update_token_amount(cur, tid, amt):
    if not amt:
        print("Nothing to add.")
        return True
    tok_val = cur.execute('SELECT tokencode FROM tokens WHERE tokencode = :tokencode', {
        'tokencode': tid}).fetchone()
    if not tok_val:
        print("Tokencode ", tid, " does not exist.")
        return False
    balance_cursor = cur.execute('SELECT amount_created FROM tokens WHERE tokencode = :tokencode', {
        'tokencode': tid})
    balance_row = balance_cursor.fetchone()
    if balance_row:
        cumul_amt = int(balance_row[0]) if balance_row[0] else 0
    else:
        cumul_amt = int(0)
    cumul_amt = cumul_amt + amt
#    cur.execute(f'''INSERT OR REPLACE INTO tokens
#				(tokencode, amount_created)
#				 VALUES (?, ?)''', (tid, cumul_amt))
    cur.execute(
        f'''UPDATE tokens SET amount_created=? WHERE tokencode=?''', (cumul_amt, tid))

    return True


def get_contract_from_address(cur, address):
    contractexec = cur.execute('SELECT * FROM contracts WHERE address = :address', {
        'address': address})
    contractdata = contractexec.fetchone()
    if not contractdata:
        print("Contract with address ", address, " does not exist.")
        return {}
    contract = {k[0]: v for k, v in list(
        zip(contractexec.description, contractdata))}
#    contract = dict(contractdata[0])
    return contract


def get_pid_from_wallet(cur, walletaddinput):
    pid_cursor = cur.execute(
        'SELECT person_id FROM person_wallet WHERE wallet_id=?', (walletaddinput, ))
    pid = pid_cursor.fetchone()
    if pid is None:
        return False
    return pid[0]


def get_block_from_cursor(cur, block_index):
    block = cur.execute(
        '''SELECT 
        block_index, hash, timestamp, status, proof,
        previous_hash, creator_wallet, 
        expected_miner, committee
        FROM blocks where block_index=?'''
    , (block_index,)).fetchone()
    if block is None:
        return None
    return {
        'block_index': block[0],
        'hash': block[1],
        'timestamp': block[2],
        'status': block[3],
        'proof': block[4],
        'previous_hash': block[5],
        'creator_wallet': block[6],
        'expected_miner': block[7],
        'committee': block[8],
    }


def create_contract_address():
    private_key_bytes = os.urandom(32)
    key = ecdsa.SigningKey.from_string(
        private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
    key_bytes = key.to_string()
    public_key = codecs.encode(key_bytes, 'hex')
    public_key_bytes = codecs.decode(public_key, 'hex')
    hash = keccak.new(digest_bits=256)
    hash.update(public_key_bytes)
    keccak_digest = hash.hexdigest()
    # this overwrites the None value in the init call, whenever on-chain contract is setup
    address = 'ct' + keccak_digest[-40:]
    return address


def input_to_dict(ipval):
    if isinstance(ipval, str):
        callparams = json.loads(ipval)
    else:
        callparams = ipval
    return callparams


def add_miner(cur, wallet_address, network_address, broadcast_timestamp, block_index):
    miner_cursor = cur.execute('SELECT last_broadcast_timestamp FROM miners where wallet_address = ?', (wallet_address, )).fetchone()
    if miner_cursor is not None:
        last_broadcast_timestamp = int(miner_cursor[0])
        if last_broadcast_timestamp > broadcast_timestamp:
            return
    cur.execute('''INSERT OR REPLACE INTO miners
				(id, wallet_address, network_address, last_broadcast_timestamp, block_index)
				 VALUES (?, ?, ?, ?, ?)''',
                 (wallet_address, wallet_address, network_address, broadcast_timestamp, block_index))

    person_id = get_pid_from_wallet(cur, wallet_address)
    if person_id is not None:
        cur.execute(f'''
        INSERT OR IGNORE INTO trust_scores
        (src_person_id, dest_person_id, score, last_time)
        VALUES (?, ?, ?, ?)''',
        (Configuration.config("NETWORK_TRUST_MANAGER_PID"), person_id,
        INITIAL_NETWORK_TRUST_SCORE, broadcast_timestamp))

def add_pid_contract_add(cur,ct_add):
    pid = get_person_id_for_wallet_address(ct_add)
    query_params = (pid, get_time_ms())
    cur.execute(f'''INSERT OR IGNORE INTO person
                        (person_id, created_time)
                        VALUES (?, ?)''', query_params)
    query_params = (pid, ct_add)
    cur.execute(f'''INSERT OR IGNORE INTO person_wallet
                    (person_id, wallet_id)
                    VALUES (?, ?)''', query_params)
    return pid

def slashing_tokens(cur,address,is_block):
    data = cur.execute(f'''select amount,staker_wallet_address from stake_ledger where wallet_address=:address''',
                          {"address": address}).fetchone()
    amount = 0
    if data is not None:
        balance = data[0]
        if balance < MIN_STAKE_AMOUNT:
            logger.warn('Balance lower than minimum required stake for wallet %s. Not slashing.', address)
            return False
        min_stake = int(Configuration.config("MIN_STAKE_AMOUNT"))
        if is_block:
            amount = min_stake
        else:
            amount = int(min_stake/int(Configuration.config("STAKE_PENALTY_RATIO")))
        actual_balance=balance
        balance = balance-amount
        deducted_amount=0
        # Transferring amount (i.e. penal amount to the zero address)
        data_json=json.loads(data[1])
        for index, value in enumerate(data_json):
            for i in value.keys():
                burn_amount=data_json[index][i]-(data_json[index][i]/actual_balance)*balance
                data_json[index][i]=(data_json[index][i]/actual_balance)*balance
                transfer_tokens_and_update_balances(cur,Configuration.config("STAKE_CT_ADDRESS"),Configuration.config("NETWORK_TREASURY_ADDRESS"),NEWRL_TOKEN_CODE,math.ceil(burn_amount))
                deducted_amount=deducted_amount+math.ceil(burn_amount)
        # updating stake_ledger table with the new updated address amount
        cur.execute(f'''UPDATE stake_ledger set amount=:amount, staker_wallet_address=:staker_wallet_address where wallet_address=:address''', {"amount": actual_balance-deducted_amount,
                                                                                           "address": address,"staker_wallet_address":json.dumps(data_json)})
        return True
    else:
        logger.info("No entry found for this address while slashing %s", address)
        return False
