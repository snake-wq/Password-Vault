# Password-Vault
![vault_setup.png](images/vault_setup.png?raw=true)
![password_vault.png](images/password_vault.png?raw=true)
A simple and secure password manager built with Python and CustomTkinter.

## Features

- **Secure storage**: All passwords are encrypted using Argon2id key derivation and Fernet (AES-128-CBC) before being saved to a `.passvault` file.
- **Master password**: Unlock the vault with a single master password (used to derive the encryption key).
- **Intuitive GUI**: Modern interface with customizable appearance.
  - Switch between `dark`, `light`, and `system` appearance modes.
  - Choose from multiple color themes: `blue`, `green`, `gold`.
- **Password entries**: Each entry can contain a service, login, password, and an optional note.
  - Add, edit, delete entries at any time.
  - Click on any field to copy its value to the clipboard.
  - Passwords are hidden by default (shown as `••••••`); click the eye button to reveal.
- **Vault initialization**: On first launch, you can either select an existing vault file or create a new one.
- **File type**: Vault files use the `.passvault` extension.

## Requirements

- Python 3.8 or higher
- [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- [cryptography](https://cryptography.io/)
- [pyperclip](https://pypi.org/project/pyperclip/)

Install dependencies:

```bash
pip install customtkinter cryptography pyperclip
```

## Usage

1. Run the application:

   ```bash
   python main.py
   ```

2. On first start, choose **Select Existing Vault** to open a `.passvault` file or **Create New Vault** to set a master password and save a new vault.

3. After unlocking, you can add, edit, or delete password entries.

## Project Structure

- `main.py` – Main application interface.
- `crypto.py` – Encryption and key derivation functions.
- `vault.py` – Reading and writing encrypted vault files.

## Security Notes

- The master password is never stored; only a random salt and the encrypted token are saved.
- Key derivation uses Argon2id with 1 iteration and 2 GiB memory cost (you may adjust these parameters for your needs).
- Passwords are kept in memory only while the vault is unlocked.

## License

This project is open-source. Feel free to use and modify it.
