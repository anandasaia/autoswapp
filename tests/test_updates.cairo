%lang starknet

@contract_interface
namespace IFactory {
    func create_pair(token0: felt, token1: felt) -> (pair: felt) {
    }

    func set_fee_to(new_fee_to: felt) {
    }

    func set_fee_to_setter(new_fee_to_setter: felt) {
    }

    func get_fee_to() -> (address: felt) {
    }

    func get_fee_to_setter() -> (address: felt) {
    }
}

@contract_interface
namespace IRouter {
    func factory() -> (address: felt) {
    }

    func sort_tokens(tokenA: felt, tokenB: felt) -> (token0: felt, token1: felt) {
    }
}

@contract_interface
namespace IProxy {
    func set_admin(new_admin: felt) {
    }

    func get_admin() -> (admin: felt) {
    }
}

@external
func __setup__{syscall_ptr: felt*, range_check_ptr}() {
    tempvar deployer_address = 123456789987654321;
    tempvar factory_address;
    tempvar router_address;
    tempvar token_0_address;
    tempvar token_1_address;
    %{
        context.deployer_address = ids.deployer_address
        context.declared_pair_proxy_class_hash = declare("contracts/PairProxy.cairo").class_hash
        context.declared_pair_class_hash = declare("contracts/Pair.cairo").class_hash
        context.declared_factory_class_hash = declare("contracts/Factory.cairo").class_hash
        context.factory_address = deploy_contract("contracts/FactoryProxy.cairo", [context.declared_factory_class_hash, context.declared_pair_proxy_class_hash, context.declared_pair_class_hash, context.deployer_address]).contract_address
        context.declared_router_class_hash = declare("contracts/Router.cairo").class_hash
        context.router_address = deploy_contract("contracts/RouterProxy.cairo", [context.declared_router_class_hash, context.factory_address, context.deployer_address]).contract_address
        context.token_0_address = deploy_contract("lib/cairo_contracts/src/openzeppelin/token/erc20/presets/ERC20Mintable.cairo", [11, 1, 18, 0, 0, context.deployer_address, context.deployer_address]).contract_address
        context.token_1_address = deploy_contract("lib/cairo_contracts/src/openzeppelin/token/erc20/presets/ERC20Mintable.cairo", [22, 2, 6, 0, 0, context.deployer_address, context.deployer_address]).contract_address
        ids.factory_address = context.factory_address
        ids.router_address = context.router_address
        ids.token_0_address = context.token_0_address
        ids.token_1_address = context.token_1_address
    %}
    let (sorted_token_0_address, sorted_token_1_address) = IRouter.sort_tokens(
        contract_address=router_address, tokenA=token_0_address, tokenB=token_1_address
    );

    let (pair_address) = IFactory.create_pair(
        contract_address=factory_address,
        token0=sorted_token_0_address,
        token1=sorted_token_1_address,
    );

    %{ context.pair_address = ids.pair_address %}
    return ();
}

@external
func test_set_fee_to_non_fee_to_setter{syscall_ptr: felt*, range_check_ptr}() {
    tempvar factory_address;

    %{ ids.factory_address = context.factory_address %}

    %{ expect_revert(error_message="Factory::set_fee_to::Caller must be fee to setter") %}
    IFactory.set_fee_to(contract_address=factory_address, new_fee_to=200);

    return ();
}

@external
func test_set_fee_to{syscall_ptr: felt*, range_check_ptr}() {
    tempvar deployer_address;
    tempvar factory_address;

    %{
        ids.deployer_address = context.deployer_address
        ids.factory_address = context.factory_address
    %}

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.factory_address) %}
    tempvar new_fee_to_address = 200;
    IFactory.set_fee_to(contract_address=factory_address, new_fee_to=new_fee_to_address);
    %{ stop_prank() %}

    let (get_fee_to_address) = IFactory.get_fee_to(contract_address=factory_address);
    assert get_fee_to_address = new_fee_to_address;

    return ();
}

@external
func test_update_fee_to_setter_non_fee_to_setter{syscall_ptr: felt*, range_check_ptr}() {
    tempvar factory_address;

    %{ ids.factory_address = context.factory_address %}

    %{ expect_revert(error_message="Factory::set_fee_to_setter::Caller must be fee to setter") %}
    IFactory.set_fee_to_setter(contract_address=factory_address, new_fee_to_setter=200);

    return ();
}

@external
func test_update_fee_to_setter_zero{syscall_ptr: felt*, range_check_ptr}() {
    tempvar deployer_address;
    tempvar factory_address;

    %{
        ids.deployer_address = context.deployer_address
        ids.factory_address = context.factory_address
    %}

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.factory_address) %}
    %{ expect_revert(error_message="Factory::set_fee_to_setter::new_fee_to_setter must be non zero") %}
    IFactory.set_fee_to_setter(contract_address=factory_address, new_fee_to_setter=0);
    %{ stop_prank() %}

    return ();
}

@external
func test_update_fee_to_setter{syscall_ptr: felt*, range_check_ptr}() {
    tempvar deployer_address;
    tempvar factory_address;

    %{
        ids.deployer_address = context.deployer_address
        ids.factory_address = context.factory_address
    %}

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.factory_address) %}
    tempvar new_fee_to_setter_address = 200;
    IFactory.set_fee_to_setter(
        contract_address=factory_address, new_fee_to_setter=new_fee_to_setter_address
    );
    %{ stop_prank() %}

    let (get_fee_to_setter_address) = IFactory.get_fee_to_setter(contract_address=factory_address);
    assert get_fee_to_setter_address = new_fee_to_setter_address;

    return ();
}

@external
func test_update_admin_non_admin{syscall_ptr: felt*, range_check_ptr}() {
    tempvar factory_address;
    tempvar router_address;
    tempvar pair_address;

    %{ 
        ids.factory_address = context.factory_address
        ids.router_address = context.router_address
        ids.pair_address = context.pair_address
    %}

    %{ expect_revert(error_message="Proxy: caller is not admin") %}
    IProxy.set_admin(contract_address=factory_address, new_admin=200);

    %{ expect_revert(error_message="Proxy: caller is not admin") %}
    IProxy.set_admin(contract_address=router_address, new_admin=200);

    %{ expect_revert(error_message="Proxy: caller is not admin") %}
    IProxy.set_admin(contract_address=pair_address, new_admin=200);

    return ();
}

@external
func test_update_admin{syscall_ptr: felt*, range_check_ptr}() {
    tempvar deployer_address;
    tempvar factory_address;
    tempvar router_address;
    tempvar pair_address;

    %{
        ids.deployer_address = context.deployer_address
        ids.factory_address = context.factory_address
        ids.router_address = context.router_address
        ids.pair_address = context.pair_address
    %}

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.factory_address) %}
    tempvar new_admin = 200;
    IProxy.set_admin(
        contract_address=factory_address, new_admin=new_admin
    );
    %{ stop_prank() %}

    let (factory_admin) = IProxy.get_admin(contract_address=factory_address);
    assert factory_admin = new_admin;

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.router_address) %}
    IProxy.set_admin(
        contract_address=router_address, new_admin=new_admin
    );
    %{ stop_prank() %}

    let (router_admin) = IProxy.get_admin(contract_address=router_address);
    assert router_admin = new_admin;

    %{ stop_prank = start_prank(ids.deployer_address, target_contract_address=ids.pair_address) %}
    IProxy.set_admin(
        contract_address=pair_address, new_admin=new_admin
    );
    %{ stop_prank() %}

    let (pair_admin) = IProxy.get_admin(contract_address=pair_address);
    assert pair_admin = new_admin;

    return ();
}
