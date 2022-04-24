from .credits import setup as cred_setup
from .management import setup as mang_setup

def setup(bot):
    cred_setup(bot)
    mang_setup(bot)