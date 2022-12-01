import asyncio
from starknet_py.contract import Contract
from starknet_py.net.gateway_client import GatewayClient
from starknet_py.net.account.account_client import AccountClient, KeyPair
from starknet_py.transactions.declare import make_declare_tx
from starknet_py.transactions.deploy import make_deploy_tx
from starknet_py.net.models import StarknetChainId
from starknet_py.net.signer.stark_curve_signer import StarkCurveSigner
from pathlib import Path
from base_funcs import *
import sys
import requests
import os

os.environ['CAIRO_PATH'] = 'lib/cairo_contracts/src/'

tokens = []
async def main():
    network_arg = sys.argv[1]
    deploy_token = None

    if network_arg == 'local':
        from config.local import fee_to_setter_address, factory_address, router_address, token_addresses_and_decimals, max_fee, token0, token1
        local_network = "http://127.0.0.1:5050"
        current_client = GatewayClient({"feeder_gateway_url": f"{local_network}/feeder_gateway", "gateway_url": f"{local_network}/gateway"})
        deployed_accounts_url = f"{local_network}/predeployed_accounts" 
        response = requests.get(deployed_accounts_url)
        deployed_accounts = response.json()
        deployer = AccountClient(
            client=current_client, 
            address=deployed_accounts[0]["address"],
            key_pair=KeyPair(private_key=int(deployed_accounts[0]["private_key"], 16), public_key=int(deployed_accounts[0]["public_key"], 16)),
            chain=StarknetChainId.TESTNET,
            supported_tx_version=1
            )
        print(deployed_accounts[0]) 
        print(f"Deployer Address: {deployer.address}, {hex(deployer.address)}")
        if fee_to_setter_address is None:
            fee_to_setter_address = deployer.address
        else:
            fee_to_setter_address = int(fee_to_setter_address, 16)
    elif network_arg == 'testnet':
        from config.testnet_none import DEPLOYER, deployer_address, fee_to_setter_address, factory_address, router_address,token_addresses_and_decimals, max_fee, token0, token1
        current_client = GatewayClient('testnet')
        key_Pair = KeyPair.from_private_key(int(DEPLOYER))
        signer = StarkCurveSigner(deployer_address, key_Pair, StarknetChainId.TESTNET)
        deployer = AccountClient(client = current_client, address = deployer_address, signer = signer, supported_tx_version=1)
        '''deployer = AccountClient(
                    client=current_client, 
                    address=deployer_address,
                    key_pair=key_Pair,
                    chain=StarknetChainId.TESTNET,
                    supported_tx_version=1
                    )'''    
        print(f"Deployer Address: {deployer.address}, {hex(deployer.address)}")
        #fee_to_setter_address = int(fee_to_setter_address, 16)
        #deployer = await Contract.from_address(current_client, deployer_address)
    elif network_arg == 'testnet2':
        from config.testnet_none import fee_to_setter_address, factory_address, router_address, token_addresses_and_decimals, max_fee
        network_url = "https://alpha4-2.starknet.io"
        current_client = GatewayClient({"feeder_gateway_url": f"{network_url}/feeder_gateway", "gateway_url": f"{network_url}/gateway"})
        fee_to_setter_address = int(fee_to_setter_address, 16)
    elif network_arg == 'mainnet':
        from config.mainnet_none import fee_to_setter_address, factory_address, router_address, token_addresses_and_decimals, max_fee
        current_client = GatewayClient('mainnet')
        fee_to_setter_address = int(fee_to_setter_address, 16)
        deploy_token = os.environ['DEPLOY_TOKEN']
    
    
    ## Deploy factory and router
    
    """if factory_address is None:
        declare_tx = make_declare_tx(compiled_contract=Path("build/Pair.json").read_text())
        declared_pair_class = await current_client.declare(declare_tx, token=deploy_token)
        declared_pair_class_hash = declared_pair_class.class_hash
        print(f"Declared pair class hash: {declared_pair_class_hash}, {hex(declared_pair_class_hash)}")
        declare_tx = make_declare_tx(compiled_contract=Path("build/PairProxy.json").read_text())
        declared_pair_proxy_class = await current_client.declare(declare_tx, token=deploy_token)
        declared_pair_proxy_class_hash = declared_pair_proxy_class.class_hash
        print(f"Declared pair proxy class hash: {declared_pair_proxy_class_hash}, {hex(declared_pair_proxy_class_hash)}")
        declare_tx = make_declare_tx(compiled_contract=Path("build/Factory.json").read_text())
        declared_factory_class = await current_client.declare(declare_tx, token=deploy_token)
        declared_factory_class_hash = declared_factory_class.class_hash
        print(f"Declared factory class hash: {declared_factory_class_hash}, {hex(declared_factory_class_hash)}")
        deploy_tx = make_deploy_tx(compiled_contract=Path("build/FactoryProxy.json").read_text(), constructor_calldata=[declared_factory_class_hash, declared_pair_proxy_class_hash, declared_pair_class_hash, fee_to_setter_address])
        deployment_result = await current_client.deploy(deploy_tx, token=deploy_token)
        await current_client.wait_for_tx(deployment_result.transaction_hash)
        factory_address = deployment_result.contract_address
    factory = Contract(address=factory_address, abi=json.loads(Path("build/Factory_abi.json").read_text()), client=current_client)
    print(f"Factory deployed: {factory.address}, {hex(factory.address)}")
    result = await factory.functions["get_fee_to_setter"].call()
    print(f"Fee to setter: {result.address}, {hex(result.address)}")"""
    
    factory = Contract(address=factory_address, abi=json.loads(Path("build/Factory_abi.json").read_text()), client=current_client)
    if router_address is None:

        declare_tx = make_declare_tx(compiled_contract=Path("build/Router.json").read_text())
        declared_router_class = await current_client.declare(declare_tx, token=deploy_token)
        declared_router_class_hash = declared_router_class.class_hash
        print(f"Declared router class hash: {declared_router_class_hash}, {hex(declared_router_class_hash)}")
        deploy_tx = make_deploy_tx(compiled_contract=Path("build/RouterProxy.json").read_text(), constructor_calldata=[declared_router_class_hash, factory.address, fee_to_setter_address])
        deployment_result = await current_client.deploy(deploy_tx, token=deploy_token)
        await current_client.wait_for_tx(deployment_result.transaction_hash)
        router_address = deployment_result.contract_address
    router = await Contract.from_address(router_address, current_client)
    print(f"Router deployed: {router.address}, {hex(router.address)}")

    # ## Deploy and Mint tokens
    
    # for (token_address, token_decimals) in token_addresses_and_decimals:
    #     token = await deploy_or_get_token(current_client, token_address, token_decimals, deployer, max_fee)
    #     tokens.append(token)

    # to_create_pairs_array = [
    #     (tokens[0], tokens[1], 10 ** 8, int((10 ** 8) / 2)), 
    #     (tokens[0], tokens[2], 10 ** 8, (10 ** 8) * 2),
    #     (tokens[0], tokens[3], 0.000162, 0.5),
    #     (tokens[3], tokens[1], 10 ** 8, int((10 ** 8) / 2)),
    #     (tokens[3], tokens[2], 10 ** 8, (10 ** 8) * 2)
    #     ]

    # for (token0, token1, amount0, amount1) in to_create_pairs_array:
        
    #     # Set pair
    #     await create_or_get_pair(current_client, factory, token0, token1, deployer, max_fee)

    #     # Add liquidity
    #     await add_liquidity_to_pair(current_client, factory, router, token0, token1, amount0, amount1, deployer, max_fee)

    #     # Swap
    token0 = await Contract.from_address(token0, deployer)
    """ if token0 is None:
        #declare_tx = make_declare_tx(compiled_contract=Path("build/dai.json").read_text())
        #declared_dai_class = await current_client.declare(declare_tx, token=deploy_token)
        #declared_dai_class_hash = declared_dai_class.class_hash
        #print(f"Declared dai class hash: {declared_dai_class_hash}, {hex(declared_dai_class_hash)}")
        deploy_tx = make_deploy_tx(compiled_contract=Path("build/dai.json").read_text(), constructor_calldata=[])
        deployment_result = await current_client.deploy(deploy_tx, token=deploy_token)
        await current_client.wait_for_tx(deployment_result.transaction_hash)
        dai_address = deployment_result.contract_address
    token0 = await Contract.from_address(dai_address, current_client)
    print(f"dai deployed: {token0.address}, {hex(token0.address)}")
    if token1 is None:
        #declare_tx = make_declare_tx(compiled_contract=Path("build/dai.json").read_text())
        #declared_dai_class = await current_client.declare(declare_tx, token=deploy_token)
        #declared_dai_class_hash = declared_dai_class.class_hash
        #print(f"Declared dai class hash: {declared_dai_class_hash}, {hex(declared_dai_class_hash)}")
        deploy_tx = make_deploy_tx(compiled_contract=Path("build/usdt.json").read_text(), constructor_calldata=[])
        deployment_result = await current_client.deploy(deploy_tx, token=deploy_token)
        await current_client.wait_for_tx(deployment_result.transaction_hash)
        usdt_address = deployment_result.contract_address
    token1 = await Contract.from_address(usdt_address, current_client)
    print(f"usdt deployed: {token1.address}, {hex(token1.address)}")"""
    #token0 = 0x03e85bfbb8e2a42b7bead9e88e9a1b19dbccf661471061807292120462396ec9
    token1 = await Contract.from_address(token1, deployer)
    #token1 = 0x005a643907b9a4bc6a55e9069c4fd5fd1f5c79a22470690f75556c4736e34426
    #amount0=100000000
    #amount1=500000000
    #await add_liquidity_to_pair(current_client, factory, router, token0, token1, amount0, amount1, deployer, max_fee)
    await swap_50PER_token0_to_token1(current_client, factory, router, token0, token1, deployer, max_fee)


if __name__ == "__main__":
    asyncio.run(main())

