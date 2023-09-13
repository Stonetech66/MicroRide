from passlib.context import CryptContext


class PasswordManager:
    pwd_hash=CryptContext(schemes=['bcrypt'], deprecated='auto')

    @classmethod
    def hash_password(cls, password):
        return cls.pwd_hash.hash(password)
    @classmethod
    def verify_password(cls, plain_password, hashed_password):
        return cls.pwd_hash.verify(plain_password, hashed_password)
    

password_manager=PasswordManager()