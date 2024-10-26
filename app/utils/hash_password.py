import bcrypt

def hash_password(password: str) -> str:
    """
    Hashes a password with salt using bcrypt.

    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password as a string.
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    """
     Checks if the provided password matches the hashed password.
     Args:
         password (str): The password to check.
         hashed_password (str): The hashed password to compare against.
     Returns:
         bool: True if the password matches, False otherwise.
     """

    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
