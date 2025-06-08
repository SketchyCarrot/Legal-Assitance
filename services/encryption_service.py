from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
import json
from typing import Any, Dict, Union
from config.security_config import SECURITY_CONFIG

class EncryptionService:
    def __init__(self):
        """Initialize encryption service with secure key generation"""
        self._encryption_key = self._generate_key()
        self._fernet = Fernet(self._encryption_key)
        self._aesgcm = AESGCM(self._generate_aes_key())

    def _generate_key(self) -> bytes:
        """Generate a secure encryption key using PBKDF2"""
        salt = os.urandom(SECURITY_CONFIG['ENCRYPTION']['SALT_LENGTH'])
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=SECURITY_CONFIG['ENCRYPTION']['KEY_LENGTH'],
            salt=salt,
            iterations=SECURITY_CONFIG['ENCRYPTION']['ITERATIONS']
        )
        key = base64.urlsafe_b64encode(kdf.derive(os.urandom(32)))
        return key

    def _generate_aes_key(self) -> bytes:
        """Generate a secure AES key"""
        return os.urandom(SECURITY_CONFIG['ENCRYPTION']['KEY_LENGTH'])

    def encrypt_data(self, data: Union[str, Dict[str, Any]], method: str = 'fernet') -> str:
        """
        Encrypt data using specified encryption method
        :param data: Data to encrypt (string or dictionary)
        :param method: Encryption method ('fernet' or 'aes-gcm')
        :return: Encrypted data as base64 string
        """
        try:
            # Convert dictionary to JSON string if necessary
            if isinstance(data, dict):
                data = json.dumps(data)

            if method == 'fernet':
                # Use Fernet for simple encryption
                encrypted_data = self._fernet.encrypt(data.encode())
                return base64.urlsafe_b64encode(encrypted_data).decode()
            
            elif method == 'aes-gcm':
                # Use AES-GCM for authenticated encryption
                nonce = os.urandom(12)
                data_bytes = data.encode()
                encrypted_data = self._aesgcm.encrypt(nonce, data_bytes, None)
                # Combine nonce and encrypted data
                combined = nonce + encrypted_data
                return base64.urlsafe_b64encode(combined).decode()
            
            else:
                raise ValueError(f"Unsupported encryption method: {method}")

        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")

    def decrypt_data(self, encrypted_data: str, method: str = 'fernet') -> Union[str, Dict[str, Any]]:
        """
        Decrypt data using specified encryption method
        :param encrypted_data: Encrypted data as base64 string
        :param method: Encryption method ('fernet' or 'aes-gcm')
        :return: Decrypted data (string or dictionary)
        """
        try:
            # Decode base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())

            if method == 'fernet':
                # Use Fernet for decryption
                decrypted_data = self._fernet.decrypt(encrypted_bytes)
                
            elif method == 'aes-gcm':
                # Extract nonce and ciphertext
                nonce = encrypted_bytes[:12]
                ciphertext = encrypted_bytes[12:]
                # Decrypt using AES-GCM
                decrypted_data = self._aesgcm.decrypt(nonce, ciphertext, None)
                
            else:
                raise ValueError(f"Unsupported encryption method: {method}")

            # Try to parse as JSON
            try:
                return json.loads(decrypted_data)
            except json.JSONDecodeError:
                return decrypted_data.decode()

        except Exception as e:
            raise EncryptionError(f"Decryption failed: {str(e)}")

    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """
        Encrypt a file
        :param file_path: Path to the file to encrypt
        :param output_path: Optional path for encrypted file
        :return: Path to encrypted file
        """
        try:
            if not output_path:
                output_path = file_path + '.encrypted'

            with open(file_path, 'rb') as f:
                file_data = f.read()

            # Generate a unique key for this file
            file_key = self._generate_key()
            file_fernet = Fernet(file_key)

            # Encrypt the file data
            encrypted_data = file_fernet.encrypt(file_data)

            # Save encrypted data and key
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)

            # Return the key along with the path
            return {
                'path': output_path,
                'key': base64.urlsafe_b64encode(file_key).decode()
            }

        except Exception as e:
            raise EncryptionError(f"File encryption failed: {str(e)}")

    def decrypt_file(self, encrypted_file_path: str, file_key: str, output_path: str = None) -> str:
        """
        Decrypt a file
        :param encrypted_file_path: Path to encrypted file
        :param file_key: Encryption key for the file
        :param output_path: Optional path for decrypted file
        :return: Path to decrypted file
        """
        try:
            if not output_path:
                output_path = encrypted_file_path.replace('.encrypted', '.decrypted')

            # Decode the file key
            key = base64.urlsafe_b64decode(file_key.encode())
            file_fernet = Fernet(key)

            # Read encrypted data
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()

            # Decrypt the data
            decrypted_data = file_fernet.decrypt(encrypted_data)

            # Save decrypted data
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)

            return output_path

        except Exception as e:
            raise EncryptionError(f"File decryption failed: {str(e)}")

    def secure_delete_file(self, file_path: str):
        """
        Securely delete a file by overwriting with random data
        :param file_path: Path to the file to delete
        """
        try:
            if not os.path.exists(file_path):
                return

            # Get file size
            file_size = os.path.getsize(file_path)

            # Overwrite file with random data multiple times
            for _ in range(3):
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))

            # Finally delete the file
            os.remove(file_path)

        except Exception as e:
            raise EncryptionError(f"Secure file deletion failed: {str(e)}")

class EncryptionError(Exception):
    """Custom exception for encryption-related errors"""
    pass 