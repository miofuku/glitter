from typing import Dict, Optional
import json
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

class DIDManager:
    def __init__(self):
        self.did_prefix = "did:glitter:"
        
    def create_did(self, public_key) -> str:
        # 将公钥序列化为 bytes
        public_bytes = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # 使用 base64 编码公钥作为 DID 的标识符部分
        did_suffix = base64.urlsafe_b64encode(public_bytes).decode('utf-8')[:32]
        return f"{self.did_prefix}{did_suffix}"
    
    def create_did_document(self, did: str, public_key) -> Dict:
        # 创建符合 W3C DID 规范的 DID Document
        public_key_jwk = self._convert_public_key_to_jwk(public_key)
        
        return {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": did,
            "verificationMethod": [{
                "id": f"{did}#keys-1",
                "type": "RsaVerificationKey2018",
                "controller": did,
                "publicKeyJwk": public_key_jwk
            }],
            "authentication": [f"{did}#keys-1"],
            "assertionMethod": [f"{did}#keys-1"]
        }
        
    def _convert_public_key_to_jwk(self, public_key) -> Dict:
        # 将公钥转换为 JWK 格式
        public_numbers = public_key.public_numbers()
        return {
            "kty": "RSA",
            "n": base64.urlsafe_b64encode(public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, byteorder='big')).decode('utf-8'),
            "e": base64.urlsafe_b64encode(public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, byteorder='big')).decode('utf-8')
        }