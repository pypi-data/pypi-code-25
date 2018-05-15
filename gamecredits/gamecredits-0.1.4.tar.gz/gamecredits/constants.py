# GameCredits network and client specific constants

# For communicating with other clients
CLIENT_DEFAULT_PORT = 40002

# For client RPC calls
CLIENT_DEFAULT_RPC_PORT = 40001

# Reward halving every xx blocks
SUBSIDY_HALVING_INTERVAL = 840000

# GameCredits network magic number
MAGIC_NUMBER = 0xFBA4C795

# Used to form paytopubkey addresses,
# when hashed using this prefix addresses start with uppercase G
PAY_TO_PUBKEY_VERSION_PREFIX = 38

# Used to form pay to script addresses,
# when hashed using this prefix addresses start with 3
PAY_TO_SCRIPT_VERSION_PREFIX = 5

# Max possible difficulty for the Proof of Work algorithm
MAX_DIFFICULTY = int("0x00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", 16)
