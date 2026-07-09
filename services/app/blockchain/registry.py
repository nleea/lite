"""web3.py client for the DocumentRegistry contract.

Loads the precompiled contract artifact (ABI + bytecode), deploys it to the local
EVM (Anvil) on first use, and persists the address in Postgres so it survives
service restarts. Exposes anchor / verify / info. Everything degrades with a clear
error if the node is unreachable.

The contract is compiled ahead of time (see contracts/DocumentRegistry.json,
produced with the official solc image) so the service needs no Solidity toolchain
at runtime — which also sidesteps solc's lack of an arm64 binary.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from pathlib import Path

from app.config import settings

logger = logging.getLogger(__name__)

_ARTIFACT_PATH = Path(__file__).parent / "contracts" / "DocumentRegistry.json"

_lock = threading.Lock()
_state: dict = {}  # cached web3 / contract / account


class BlockchainUnavailable(RuntimeError):
    """Raised when the EVM node cannot be reached."""


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _artifact() -> tuple[list, str]:
    data = json.loads(_ARTIFACT_PATH.read_text(encoding="utf-8"))
    return data["abi"], data["bytecode"]


def _web3():
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(settings.web3_rpc_url))
    if not w3.is_connected():
        raise BlockchainUnavailable(f"EVM node not reachable at {settings.web3_rpc_url}")
    return w3


def _load_persisted(w3):
    """Reuse a previously deployed contract if it still has code on-chain.

    The stored ABI on the deployment row is authoritative, so no ABI arg here.
    """
    from app.blockchain.models import BlockchainDeployment
    from app.db import SessionLocal

    with SessionLocal() as session:
        row = session.get(BlockchainDeployment, settings.web3_chain_id)
        if row and w3.eth.get_code(w3.to_checksum_address(row.address)) not in (b"", b"0x"):
            return w3.eth.contract(
                address=w3.to_checksum_address(row.address), abi=json.loads(row.abi)
            )
    return None


def _persist(address: str, abi: list) -> None:
    from app.blockchain.models import BlockchainDeployment
    from app.db import SessionLocal

    with SessionLocal() as session:
        row = session.get(BlockchainDeployment, settings.web3_chain_id)
        if row is None:
            row = BlockchainDeployment(chain_id=settings.web3_chain_id)
            session.add(row)
        row.address = address
        row.abi = json.dumps(abi)
        session.commit()


def _send(w3, account, tx):
    # build_transaction already populates gas and EIP-1559 fee fields; we only
    # ensure sender/nonce/chain. Setting gasPrice here would conflict with the
    # type-2 (maxFeePerGas) fields Anvil expects.
    tx.setdefault("from", account.address)
    tx.setdefault("nonce", w3.eth.get_transaction_count(account.address))
    tx.setdefault("chainId", settings.web3_chain_id)
    signed = account.sign_transaction(tx)
    raw = getattr(signed, "raw_transaction", None) or signed.rawTransaction
    tx_hash = w3.eth.send_raw_transaction(raw)
    return w3.eth.wait_for_transaction_receipt(tx_hash)


def _init() -> dict:
    w3 = _web3()
    account = w3.eth.account.from_key(settings.web3_private_key)
    abi, bytecode = _artifact()

    contract = _load_persisted(w3)
    if contract is None:
        factory = w3.eth.contract(abi=abi, bytecode=bytecode)
        tx = factory.constructor().build_transaction(
            {"from": account.address, "nonce": w3.eth.get_transaction_count(account.address)}
        )
        receipt = _send(w3, account, tx)
        address = receipt.contractAddress
        _persist(address, abi)
        logger.info("Deployed DocumentRegistry at %s", address)
        contract = w3.eth.contract(address=address, abi=abi)
    else:
        logger.info("Reusing DocumentRegistry at %s", contract.address)

    return {"w3": w3, "account": account, "contract": contract}


def _get() -> dict:
    with _lock:
        if not _state:
            _state.update(_init())
        return _state


def _hash_bytes(hex_hash: str) -> bytes:
    return bytes.fromhex(hex_hash.removeprefix("0x"))


def anchor(pdf_hash_hex: str) -> dict:
    """Anchor a SHA-256 hex hash on-chain. Returns the receipt details."""
    state = _get()
    w3, account, contract = state["w3"], state["account"], state["contract"]
    tx = contract.functions.anchor(_hash_bytes(pdf_hash_hex)).build_transaction(
        {"from": account.address, "nonce": w3.eth.get_transaction_count(account.address)}
    )
    receipt = _send(w3, account, tx)
    anchored_at = contract.functions.verify(_hash_bytes(pdf_hash_hex)).call()
    return {
        "hash": pdf_hash_hex,
        "tx_hash": receipt.transactionHash.hex(),
        "block": receipt.blockNumber,
        "anchored_at": int(anchored_at),
    }


def verify(pdf_hash_hex: str) -> dict:
    """Return whether a hash is anchored and when."""
    contract = _get()["contract"]
    anchored_at = int(contract.functions.verify(_hash_bytes(pdf_hash_hex)).call())
    return {"hash": pdf_hash_hex, "anchored": anchored_at > 0, "anchored_at": anchored_at}


def info() -> dict:
    """Contract address, chain id and node reachability."""
    try:
        state = _get()
        return {
            "connected": True,
            "chain_id": settings.web3_chain_id,
            "contract_address": state["contract"].address,
            "rpc_url": settings.web3_rpc_url,
        }
    except BlockchainUnavailable as exc:
        return {"connected": False, "detail": str(exc), "rpc_url": settings.web3_rpc_url}


def ensure_ready() -> None:
    """Deploy/load the contract eagerly (called at startup)."""
    _get()
