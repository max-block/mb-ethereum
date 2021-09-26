Usage: cli [OPTIONS] COMMAND [ARGS]...

Options:
  -c, --config / --no-config  Print config and exit
  -n, --node TEXT             List of JSON RPC nodes, it overwrites node/nodes
                              field in config
  --version                   Show the version and exit
  --help                      Show this message and exit

Commands:
  account              Print nonce, eth and token balances
  cancel               Cancel a pending tx
  contract-call        Do eth_call to a contract
  contract-signatures  Print all contract signatures
  contract-tx          Send tx to a contract method
  convert              Convert value between wei, gwei, ether
  decode-bytes         Decode bytes
  decode-raw-tx        Decode a raw tx hex
  decode-tx-input      Decode tx input
  deploy               Deploy a contract
  dump-help            Dump help for all subcommands
  encode-abi           Encode API for data: types and args
  example              Print config or arg example for a module and exit
  find-address         Find ethereum addresses in a path
  mnemonic             Generate eth accounts based on mnemonic
  node                 Print RPC nodes info
  private-key          Print address for a private key
  rpc                  Do JSON-RPC call to a node
  send                 Send txs
  sign                 Sign a tx
  solc                 Compile a solidity file
  speedup              Speed up a pending tx
  transfer-all         Transfer all ether or tokens to one address

Usage: cli account [OPTIONS] CONFIG_PATH

  Print nonce, eth and token balances

Options:
  --no-spinner  Don't use a spinner
  --help        Show this message and exit.

-------------------------

Usage: cli cancel [OPTIONS] CONFIG_PATH

  Cancel a pending tx

Options:
  -b, --broadcast  Broadcast a tx
  --help           Show this message and exit.

-------------------------

Usage: cli contract-call [OPTIONS] CONFIG_PATH

  Do eth_call to a contract

Options:
  --print-data / --no-print-data
  --help                          Show this message and exit.

-------------------------

Usage: cli contract-signatures [OPTIONS] ABI_PATH

  Print all contract signatures

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli contract-tx [OPTIONS] CONFIG_PATH

  Send tx to a contract method

Options:
  -b, --broadcast  Broadcast txs
  --help           Show this message and exit.

-------------------------

Usage: cli convert [OPTIONS] VALUE

  Convert value between wei, gwei, ether

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli decode-bytes [OPTIONS] TYPES DATA

  Decode bytes

  TYPES is a list of types, for example: '["address", "uint256"]'

  DATA is a hex data

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli decode-raw-tx [OPTIONS] RAW_TX

  Decode a raw tx hex

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli decode-tx-input [OPTIONS] CONFIG_PATH

  Decode tx input

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli deploy [OPTIONS] CONFIG_PATH

  Deploy a contract

Options:
  -b, --broadcast  Broadcast tx
  --help           Show this message and exit.

-------------------------

Usage: cli encode-abi [OPTIONS] TYPES ARGS

  Encode API for data: types and args

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli example [OPTIONS] {account|cancel|contract-call|contract-
                   tx|convert|decode-bytes|decode-raw-
                   tx|node|rpc|send|deploy|sign|speedup|transfer-all}

  Print config or arg example for a module and exit

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli find-address [OPTIONS] PATH

  Find ethereum addresses in a path

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli mnemonic [OPTIONS]

  Generate eth accounts based on mnemonic

Options:
  -m, --mnemonic TEXT
  --help               Show this message and exit.

-------------------------

Usage: cli node [OPTIONS] CONFIG_PATH

  Print RPC nodes info

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli private-key [OPTIONS] PRIVATE_KEY

  Print address for a private key

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli rpc [OPTIONS] CONFIG_PATH

  Do JSON-RPC call to a node

Options:
  --curl / --no-curl  Print curl request and exit
  --help              Show this message and exit.

-------------------------

Usage: cli send [OPTIONS] CONFIG_PATH

  Send txs

Options:
  -b, --broadcast  Broadcast txs
  --help           Show this message and exit.

-------------------------

Usage: cli sign [OPTIONS] CONFIG_PATH

  Sign a tx

Options:
  --help  Show this message and exit.

-------------------------

Usage: cli solc [OPTIONS] CONTRACT_FILE

  Compile a solidity file

Options:
  --bin / --no-bin
  --abi / --no-abi
  --optimize / --no-optimize
  --output TEXT
  --help                      Show this message and exit.

-------------------------

Usage: cli speedup [OPTIONS] CONFIG_PATH

  Speed up a pending tx

Options:
  -b, --broadcast  Broadcast a tx
  --help           Show this message and exit.

-------------------------

Usage: cli transfer-all [OPTIONS] CONFIG_PATH

  Transfer all ether or tokens to one address

Options:
  -b, --broadcast  Broadcast tx
  --help           Show this message and exit.

-------------------------

Usage: cli dump-help [OPTIONS]

  Dump help for all subcommands

Options:
  --help  Show this message and exit.

-------------------------
