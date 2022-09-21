import os

from app.ntypes import NEWRL_TOKEN_DECIMAL


NEWRL_ENV = os.environ.get('NEWRL_ENV')

if NEWRL_ENV == 'testnet':
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    NETWORK_TRUST_MANAGER_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    NETWORK_TRUST_MANAGER_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    NETWORK_TRUST_MANAGER_PID = 'pi10d84aa634ba8751804ca4e02134696a75ae3515'
    ASQI_PID = 'pi10d84aa634ba8751804ca4e02134696a75ae3515'
    ASQI_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'  # TODO - Need to store contract address instead
    ASQI_WALLET_DAO = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    ASQI_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    FOUNDATION_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'  # TODO - Need to store contract address instead
    FOUNDATION_WALLET_DAO = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    FOUNDATION_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    SENTINEL_NODE_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    SENTINEL_NODE_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    DAO_MANAGER = 'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
    NETWORK_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb8'
    ASQI_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64fb9'
    FOUNDATION_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64fc1'
    ASQI_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb9'
    FOUNDATION_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec1'
    CONFIG_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec2'
    STAKE_COOLDOWN_MS = 600000
    MIN_STAKE_AMOUNT = 100000 * pow(10, NEWRL_TOKEN_DECIMAL)
    STAKE_PENALTY_RATIO = 10
    STAKE_CT_ADDRESS = 'ctcdb91798f3022dee388b7ad55eeea527f98caee4'
    MEMBER_WALLET_LIST = [
        '0xdc5ce2dd2103635210591bd43cf1a95c9406c1b2',
        '0x8159aacfd3e3d9afbb9dff37bf1896e0479d19a6',
        '0x7633fb937d7970e1668a16999453bbb64a30fcf1',
        '0xd506831f17f6936e27bd1a9187efd48c23c0bcbb',
        '0xbc54ef523d92b6acaf16a49b328cfffca84503ca',
        '0x3eb52110ced4da0023fb21859db33a42954f7530',
        '0x4dba43d40b869f6ba9f7b0ea5c5ef054debdacc3',
        '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
    ]
elif NEWRL_ENV == 'mainnet':
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x5d5e00b81bf2018d4db56b6ff6bf67bd77889450'
    NETWORK_TRUST_MANAGER_WALLET = '0xaecdbe3d58a2b9e20445210678ac5e7ebf8b6172'
    NETWORK_TRUST_MANAGER_PUBLIC = '+Yv7oDycZkuxJUByT1TqnZjMpTvKWr/FAiEt5ygzyeXOMwS+ZJqmO/+f9R2W6o3OSR+XtZAjyr6eKRkMc1qTHg=='
    NETWORK_TRUST_MANAGER_PID = 'pi69e3fc1a079b3b6b4d23958ef9941c3ed8431b7d'
    ASQI_WALLET_DAO = '0x5ddf89d2d98ac025df644cc14f87d55a324c988e'
    ASQI_WALLET = 'ctb020e608d11c235724e676d021a08f8da6c64eb9'
    ASQI_WALLET_PUBLIC = '42EiFw0rSZpYklK4qtjpq8n4adGG6JZEktJwGaQ+ysW0sPavd947zjQLebEH0/YqL+qnigTjVlwcjJ+GQ4ltbg=='
    FOUNDATION_WALLET = '0xab541ab69ab595d6fec84e1238f842cc53401cab'
    FOUNDATION_WALLET_DAO = 'ctb020e608d11c235724e676d021a08f8da6c64ec1'
    FOUNDATION_WALLET_PUBLIC = 'a10A//+XhIIXvw2YyHlu6bb6S5W4lJ6DfRkZdtUmt1Qwecn1mL+Q/5sjOxeMEAWXl56Sig91FYz9HBrqokGPzg=='
    SENTINEL_NODE_WALLET = '0x02245e77732cd9fa4068eca57d0fc1767b02becb'
    SENTINEL_NODE_WALLET_PUBLIC = 'LLspogALME+HMU4aceFZUS1FQmroW1o4GSbOg8NAZkFEknGH7VpuZ2V8gIdAAFRaTyUVXW+3sAN8suGPfX4seg=='
    DAO_MANAGER = 'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
    TREASURY_CONTRACT_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb8'
    STAKE_COOLDOWN_MS = 2419200000
    MIN_STAKE_AMOUNT=100000
    STAKE_PENALTY_RATIO=10
    STAKE_CT_ADDRESS='ctcdb91798f3022dee388b7ad55eeea527f98caee4'
    ASQI_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb9'
    NEWRL_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec1'
    CONFIG_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec2'
else:
    ZERO_ADDRESS = '0x0000000000000000000000000000000000000000'
    TREASURY_WALLET_ADDRESS = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    NETWORK_TRUST_MANAGER_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    NETWORK_TRUST_MANAGER_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    NETWORK_TRUST_MANAGER_PID = 'pi10d84aa634ba8751804ca4e02134696a75ae3515'
    ASQI_PID = 'pi10d84aa634ba8751804ca4e02134696a75ae3515'
    ASQI_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'  # TODO - Need to store contract address instead
    ASQI_WALLET_DAO = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    ASQI_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    FOUNDATION_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'  # TODO - Need to store contract address instead
    FOUNDATION_WALLET_DAO = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    FOUNDATION_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    SENTINEL_NODE_WALLET = '0x667663f36ac08e78bbf259f1361f02dc7dad593b'
    SENTINEL_NODE_WALLET_PUBLIC = '09c191748cc60b43839b273083cc565811c26f5ce54b17ed4b4a17c61e7ad6b880fc7ac3081b9c0cf28756ea21ce501789b59e8f9103f3668ccf2c86108628ee'
    DAO_MANAGER = 'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
    NETWORK_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb8'
    ASQI_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64fb9'
    FOUNDATION_TREASURY_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64fc1'
    ASQI_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64eb9'
    FOUNDATION_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec1'
    CONFIG_DAO_ADDRESS = 'ctb020e608d11c235724e676d021a08f8da6c64ec2'
    STAKE_COOLDOWN_MS=600000
    MIN_STAKE_AMOUNT=100000 * pow(10, NEWRL_TOKEN_DECIMAL)
    STAKE_PENALTY_RATIO=10
    STAKE_CT_ADDRESS='ctcdb91798f3022dee388b7ad55eeea527f98caee4'
    MEMBER_WALLET_LIST = [
        '0xdc5ce2dd2103635210591bd43cf1a95c9406c1b2',
        '0x8159aacfd3e3d9afbb9dff37bf1896e0479d19a6',
        '0x7633fb937d7970e1668a16999453bbb64a30fcf1',
        '0xd506831f17f6936e27bd1a9187efd48c23c0bcbb',
        '0xbc54ef523d92b6acaf16a49b328cfffca84503ca',
        '0x3eb52110ced4da0023fb21859db33a42954f7530',
        '0x4dba43d40b869f6ba9f7b0ea5c5ef054debdacc3',
        '0x667663f36ac08e78bbf259f1361f02dc7dad593b',
        'ct9dc895fe5905dc73a2273e70be077bf3e94ea3b7'
    ]