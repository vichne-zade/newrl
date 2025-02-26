import logging
from random import randint
import sys
import threading
import uvicorn
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from starlette.requests import Request
from app.codes.crypto import calculate_hash
from app.codes.log_config import get_past_log_content, logGenerator
from sse_starlette.sse import EventSourceResponse
from fastapi.responses import PlainTextResponse

from app.codes.chainscanner import download_chain, download_state, get_config
from app.codes.clock.global_time import get_time_stats
from app.codes.fs.mempool_manager import clear_mempool
from app.codes.p2p.peers import add_peer, clear_peers, get_peers, init_bootstrap_nodes, remove_dead_peers, update_software
from app.codes.p2p.sync_chain import get_blocks, get_last_block_index, quick_sync, sync_chain_from_node, sync_chain_from_peers
from app.codes.p2p.sync_mempool import list_mempool_transactions, sync_mempool_transactions
from app.codes.timers import SYNC_STATUS
from app.codes.updater import TIMERS, get_timers
from app.codes.utils import get_last_block_hash
from app.constants import SOFTWARE_VERSION
from app.migrations.init_db import clear_state_and_make_from_archive, revert_chain
from app.codes.p2p.peers import call_api_on_peers
from app.codes.auth.auth import get_node_wallet_public
from app.codes.minermanager import add_miners_as_peers, broadcast_miner_update, get_miner_info
from app.codes.dbmanager import snapshot_schedule, get_snapshot_last_block_index


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()

p2p_tag = 'System'


@router.get("/get-node-info", tags=[p2p_tag])
async def get_node_info():
    last_block = get_last_block_hash()
    if last_block is None:
        last_block_index = 0
    else:
        last_block_index = last_block['index']
    node_info = {
        'software_version': SOFTWARE_VERSION,
        'wallet': get_node_wallet_public(),
        'time': get_time_stats(),
        'last_block': last_block,
        'timers': get_timers(),
        'snapshot': {
            'snapshot_schedule': snapshot_schedule,
            'snapshot_last_block': get_snapshot_last_block_index()
        },
        'miners': get_miner_info(),
        'peers': get_peers(),
        # 'recent_blocks': get_blocks(list(range(last_block_index - 5, last_block_index))),
        'mempool_transactions': list_mempool_transactions()[-10:],
    }
    return node_info


@router.get("/download-chain", tags=[p2p_tag])
def download_chain_api():
    return download_chain()


@router.get("/download-state", tags=[p2p_tag])
def download_state_api():
    return download_state()


@router.post("/sync-mempool-transactions", tags=[p2p_tag])
def sync_mempool_transactions_api():
    return sync_mempool_transactions()


@router.post("/sync-chain-from-node", tags=[p2p_tag])
def sync_chain_from_node_api(url: str = 'https://newrl-devnet1.herokuapp.com'):
    try:
        return sync_chain_from_node(url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/quick-sync-chain-from-node", tags=[p2p_tag])
def sync_chain_from_node_api(api_key, url: str = 'http://archive1-mainnet.newrl.net:8456'):
    if calculate_hash(api_key) != '4a01127180cb827a4752abe578b47cbe23ba677037b5bb0cd420549bdb4a274d':
        return {'status': 'INVALID_KEY'}
    try:
        quick_sync(url + '/get-newrl-db')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync-chain-from-peers", tags=[p2p_tag])
async def sync_chain_from_peers_api():
    return sync_chain_from_peers(force_sync=True)


@router.post("/initiate-peer-connection", tags=[p2p_tag])
def initiate_peer_api(address: str):
    "Test only, used to first connect a client"
    return add_peer(address)

@router.get("/config", tags=[p2p_tag])
def get_config_api():
    return get_config()
    

@router.post("/update-software", tags=[p2p_tag])
def update_software_api(propogate: bool = False):
    # update_software(propogate)
    timer = threading.Timer(randint(30, 120), update_software, [propogate])
    timer.start()
    return {'status': 'SUCCESS'}


@router.get('/stream-logs',tags=[p2p_tag])
async def run(request: Request):
    event_generator = logGenerator(request)
    return EventSourceResponse(event_generator)


@router.get('/get-old-logs',tags=[p2p_tag], response_class=PlainTextResponse)
async def get_old_logs_api():
    return get_past_log_content()


@router.get("/get-status", tags=[p2p_tag])
def get_status_api():
    return {
        'up': True,
        'timers': get_timers(),
    }

@router.post("/remove-dead-peers", tags=[p2p_tag])
def get_status_api():
    add_miners_as_peers()
    remove_dead_peers()
    return {'status': 'SUCCESS'}


@router.post("/init-nodes", tags=[p2p_tag])
def get_status_api():
    init_bootstrap_nodes()
    return {'status': 'SUCCESS'}


@router.post("/clear-mempool", tags=[p2p_tag])
def clear_mempool_api(req: Request):
    return clear_mempool()


@router.post("/broadcast-miner-update", tags=[p2p_tag])
def broadcast_miner_update_api():
    return broadcast_miner_update()


# @router.post("/clear-db-test-only", tags=[p2p_tag])
# def clear_db_api():
#     """ For testing only. To be removed. Clear and initialise a fresh db """
#     clear_db()
#     init_db()
#     return True


# @router.post("/clear-peers", tags=[p2p_tag])
# def clear_peer_api(req: Request):
#     return clear_peers()


# @router.post("/turn-off-mining-clock", tags=[p2p_tag])
# def switch_mining_clock_api():
#     global TIMERS

#     if TIMERS['mining_timer'] is not None:
#         print('Turning off mining clock')
#         TIMERS['mining_timer'].cancel()
#         return {'status': 'SUCCESS'}
#     return {'status': 'FAILURE', 'message': 'Mining clock not running'}


@router.post("/revert-chain", tags=[p2p_tag])
def revert_chain_api(api_key, block_index: int, propogate: bool = False):
    if calculate_hash(api_key) != '4a01127180cb827a4752abe578b47cbe23ba677037b5bb0cd420549bdb4a274d':
        return {'status': 'INVALID_KEY'}
    revert_chain(block_index)
    if propogate:
        call_api_on_peers(f'/revert-chain?block_index={block_index}')
    return {'status': 'SUCCESS'}

@router.post("/make-state-from-archive", tags=[p2p_tag])
def make_state_from_archive_api(api_key):
    if calculate_hash(api_key) != '4a01127180cb827a4752abe578b47cbe23ba677037b5bb0cd420549bdb4a274d':
        return {'status': 'INVALID_KEY'}
    SYNC_STATUS['IS_SYNCING'] = True
    try:
        clear_state_and_make_from_archive()
    except:
        print('Error making state from archive')
    SYNC_STATUS['IS_SYNCING'] = False
    return {'status': 'SUCCESS'}
