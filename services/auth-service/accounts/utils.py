import hashlib


def hash_token(token_str):
    """Nunca guardamos el refresh token en texto plano, solo este hash."""
    return hashlib.sha256(token_str.encode('utf-8')).hexdigest()