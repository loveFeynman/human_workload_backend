from cosmpy.aerial.client import LedgerClient, NetworkConfig
from cosmpy.aerial.contract import LedgerContract
from cosmpy.aerial.wallet import LocalWallet
from cosmpy.crypto.keypairs import PrivateKey
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins
import pickle
import base64


cfg = NetworkConfig(
    chain_id="testhuman",
    url="grpc+http://142.132.197.4:9090",
    fee_minimum_gas_price=1,
    fee_denomination="uheart",
    staking_denomination="uheart",
)
client = LedgerClient(cfg)

contractAddr = "human1rshdhvvhra8gl3ywhpgtd29aythlt9tjzdv648nq3hl922499cgqx5zjzk"
contract = LedgerContract(None, client, contractAddr)


def encode(obj):
    string = pickle.dumps(obj)
    return base64.b64encode(string).decode('utf-8')


def query_execution_status(workload_id, signature_hash, pubkey_base64):
    result = contract.query({
        "get_authorized_workload": {
            "msg": workload_id,
            "signature_hash": signature_hash,
            "pubkey_base64": pubkey_base64
        }
    })

    return result

def update_status(workload_id, mnemonic, signature_hash, pubkey_base64):
    seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
    bip44_def_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.COSMOS).DeriveDefaultPath()

    wallet = LocalWallet(PrivateKey(bip44_def_ctx.PrivateKey().Raw().ToBytes()), prefix="human")

    contract.execute(
        {
            "update_workload_status": {
                "msg": workload_id,
                "signature": signature_hash,
                "pubkey": pubkey_base64
            }
        },
        wallet,
    ).wait_to_complete()


