# Bitshares Wallet App for Ledger Nano S

This is the app that runs on the Ledger Nano S device and signs transactions recieved via USB from a host wallet interface.  It also manages your keys, safeguarding the private keys and deriving the public and private keys from the wallet seed, following [BIP-0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki) and [SLIP-0048](https://github.com/satoshilabs/slips/blob/master/slip-0048.md).

A set of python scripts are provided to allow command-line interaction with the device, to request the signing of transactions read in from a file in JSON format.  The main purpose of the app, however, is to be a back-end to a more sophisticated wallet interface, and these scripts are primarily intended to provide a reference for developers developing GUI wallets.

The app follows the specification available in the [doc/](/doc/) folder, which documents the communication protocol with the device.

To use the generic wallet via the scripts, refer to `signTransaction.py`, `getPublicKey.py`.  Some examples are given below.

### Features:

* Processes serialized transactions to decode and display parameters of recognized BitShares operations, so that the user may be assured that the transaction is as intended before signing.
* Can process transactions that contain multiple operations (currently capped at four).
* For unrecognized operations, displays a warning that the details cannot be extracted, but still allows the user to sign the transaction if they wish.

### Supported Operations:

The following operations are supported in-device, and will show details of the operation on-screen.  Support for additional operations beyond those listed here will be an on-going effort.

* Transfer
* Limit Order Create
* Limit Order Cancel
* Account Update
* Account Upgrade

## Installing a GUI wallet / front end

GUI wallet front-end support for Ledger Nano S is being developed independently by multiple wallet developers.  This repository contains the back-end app for your Nano that the wallets will connect to via USB.  As such, this repository is intended primarily for developers and wallet integrators.  If you are a regular user, then it is anticipated that by the time the GUI apps are ready, this back-end app will be available for download directly to your device via the Ledger Live app store.  You will not need to get the app from here.

A list of supporting GUI apps will be added here when available.

## How to install the developer version

If you are installing the app from this repository, you will need a development environment to support compiling the app and loading onto your Ledger Nano S device.

### Configuring Ledger build environment with Ledger-Vagrant

A ready-to-use build environment hosted in a virtual machine is available via [fix/ledger-vagrant](https://github.com/fix/ledger-vagrant).  To use it, you will need [Vagrant](https://www.vagrantup.com) and [VirtualBox](https://www.virtualbox.org) on your build machine.  Then run the following:

```
git clone https://github.com/fix/ledger-vagrant
cd ledger-vagrant
vagrant up
```

This will take a few minutes to install.  For more info on setting up the build environment, refer to [fix/ledger-vagrant](https://github.com/fix/ledger-vagrant).  Once the virtual machine is up and running, you can connect to it with:

```
vagrant ssh
```

### Install python-bitshares

[Python-bitshares](https://github.com/bitshares/python-bitshares) is a python library that allows working with BitShares transactions, and is required by the example python scripts provided with this project.  It is not strictly needed to compile and install the device app, but if you wish to use the sample scripts to test the app, you will need python-bitshares.

If not already connected, connect to your virtual mahine with:

```
vagrant ssh
```

Then install required dependencies and the library with:

```
sudo apt-get install libffi-dev libssl-dev python-dev python3-dev python3-pip
pip3 install --upgrade setuptools
pip3 install bitshares
```

Note that python-bitshares is a Python 3 project, and that it's important to use `pip3` and not `pip` to do the installs.

### Install additional dependencies

A few things that we need are missing from the ledger-vagrant pre-configured build environment.  If you intend to use the included python scripts, then also install the following:

```
pip3 install base58 asn1 enum34
pip3 install ledgerblue
```

Note that installing `ledgerblue` may seem redundant since ledger-vagrant installs it, but note that we are installing the Python 3 version of it here, and our scripts won't work without it.  (Ledger-vagrant only installs the Python 2.7 version.)

### Compile and load Ledger app

With the build environment configured, we can now clone, compile, and load ledger-app-bitshares.  Note that when you installed ledger-vagrant, it created an `apps/` directory that is accessible in both the host filesystem and the virtual machine. 

* Clone the app repository, under the apps/ folder:

```
cd apps/
git clone https://github.com/christophersanborn/ledger-app-bitshares

```

* Now connect to the virtual machine with `vagrant ssh` and compile the app: 

```
cd apps/ledger-app-bitshares
make clean
make
```

* Next connect your Ledger Nano S to your computer:
  * Install the app on your Ledger with: `make load`
  * Remove the app from the Ledger with: `make delete`

### Testing the app

Once loaded on your device, the app shows up in the Nano's dashboard as "BitShares" with the familiar icon.  Select it and start the app by pressing both buttons on the Nano simultaneously.

#### BitShares wallet addresses:

You can retrieve a BitShares public key managed by the Nano with `getPublicKey.py`.  Examples:

```
python3 getPublicKey.py
python3 getPublicKey.py --path "48'/1'/0'/0'/0'"
```

In the first instance the default derivation path is used.  In the second instance, a specific path is requested.  Note that the app is constrained to use paths beginning with 48'/1'/.  The public key is also shown on screen on the device.

You can see a range of addresses and an illustration of the SLIP-0048 scheme with `testDerivationPathGeneration.py`:

```
python3 testDerivationPathGeneration.py
```

#### Signing transactions:

Some example transactions are included as .json files in the `example-tx` directory.  We can ask the BitShares app on the Nano to sign one of these transactions with the `signTransaction.py` python script.  Examples:

```
python3 signTransaction.py --file=example-tx/tx_transfer.json
python3 signTransaction.py --file=example-tx/tx_limit_order_create.json
```

Details of the transaction will be shown on the Ledger's screen, and the user will be able to accept or reject the transaction.

#### Developer notes:

* The python scripts will show a hex representation of the bytes exchanged with the device in the terminal output.  This will be useful in confirming your understanding of the communication protocol with the device, and help with GUI wallet integration efforts.

* Developers may find useful the "debugging firmware", which enables streaming of `stdout` over the USB connection, allowing debugging output via a PRINTF macro.  Instructions for installing and using this firmware are [here](https://ledger.readthedocs.io/en/latest/userspace/debugging.html)
