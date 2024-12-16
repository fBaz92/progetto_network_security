# certificates.py
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import base64
from typing import Tuple, Optional

@dataclass
class Certificate:
    """Certificate class for storing public key and identity information"""
    subject: str
    public_key: Tuple[int, int]
    issuer: str
    valid_from: datetime
    valid_until: datetime
    signature: Optional[str] = None

    def to_dict(self):
        """Convert certificate to dictionary for serialization"""
        return {
            "subject": self.subject,
            "public_key": list(self.public_key),
            "issuer": self.issuer,
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat(),
            "signature": self.signature
        }

    @classmethod
    def from_dict(cls, data):
        """Create certificate from dictionary"""
        return cls(
            subject=data["subject"],
            public_key=tuple(data["public_key"]),
            issuer=data["issuer"],
            valid_from=datetime.fromisoformat(data["valid_from"]),
            valid_until=datetime.fromisoformat(data["valid_until"]),
            signature=data.get("signature")
        )

    def to_string(self):
        """Convert certificate to string for signing (excluding signature)"""
        cert_dict = self.to_dict()
        cert_dict.pop("signature", None)  # Remove signature before converting to string
        return json.dumps(cert_dict, sort_keys=True)