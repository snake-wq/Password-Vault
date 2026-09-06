import pickle
from os.path import isfile

def read(file: str) -> None | object:
    if not isfile(file):
        return None

    with open(file, "rb") as file:
        loaded_data = pickle.load(file)
        return loaded_data

def write(salt: bytes, token: bytes, file: str):
    vault_data = {"salt": salt, "token": token}
    with open(file, "wb") as file:
        pickle.dump(vault_data, file)