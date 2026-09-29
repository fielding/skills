"""AES-256-GCM sealing for notes at rest.

Keys are derived from the user's passphrase with scrypt (N=2**15, r=8, p=1) and never
stored. Each note is sealed as nonce || ciphertext || tag.
"""


def derive_key(passphrase: str) -> bytes:
    """Derive a 32-byte key from the passphrase with scrypt."""
    raise NotImplementedError("TODO: scrypt KDF")


def encrypt(plaintext: bytes, key: bytes) -> bytes:
    """Seal plaintext with AES-256-GCM; returns nonce || ciphertext || tag."""
    raise NotImplementedError("TODO: wire AES-GCM")


def decrypt(blob: bytes, key: bytes) -> bytes:
    """Open a sealed blob produced by encrypt()."""
    raise NotImplementedError("TODO: wire AES-GCM")
