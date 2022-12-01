let (deadline) = get_block_timestamp()
let (local path : felt*) = alloc()
assert [path] = DAI_address
assert [path+1] = ETH_address
let path_len = 2
IRouter.swap_exact_tokens_for_tokens(contract_address = router, amountIn = amount, amountOutMin = amountOutMin, path_len = path_len, path = path, to = contract_address, deadline = deadline)