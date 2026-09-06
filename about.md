# Интерфейс
CustomTkinter

# Безопасность
Мастер пароль -> Хешируем -> Пароль шифрования


# Encryption
https://pypi.org/project/cryptography/ - cryptography.fernet

Implementation (https://github.com/fernet/spec/blob/master/Spec.md)

- Fernet is built on top of a number of standard cryptographic primitives. Specifically it uses:
- AES in CBC mode with a 128-bit key for encryption; using PKCS7 padding.
- HMAC using SHA256 for authentication.
- Initialization vectors are generated using os.urandom().