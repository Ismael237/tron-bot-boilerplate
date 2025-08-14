from database.database import SessionLocal
from database.models import UserWallet
from blockchain.tron_client import generate_wallet
from utils.encryption import encrypt_data


def get_or_create_wallet(user_id):
    session = SessionLocal()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()
    if wallet:
        session.close()
        return wallet
    address, privkey = generate_wallet()
    encrypted_key = encrypt_data(privkey.encode())
    wallet = UserWallet(
        user_id=user_id,
        address=address,
        private_key_encrypted=encrypted_key
    )
    session.add(wallet)
    session.commit()
    session.close()
    return wallet

def get_wallet(user_id):
    session = SessionLocal()
    wallet = session.query(UserWallet).filter_by(user_id=user_id).first()
    session.close()
    return wallet 