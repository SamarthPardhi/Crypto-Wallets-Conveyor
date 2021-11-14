#User's data with sha256 hashes of passcodes
users=[
    {
        'type':'admin',
        'name':'dev',
        'id':'A01',
        'hash':'abcdc8444f56d3d4f576d3e3aa042de3e7ac830a8df309cb97c1048bc2ca7cac' 
    },
    {
        'type':'admin',
        'name':'john',
        'id':'A02',
        'hash':'7e5447fb7b997af81702370446ecf652e16533d643eb4979337e289054d8c339' #joHn$d
    },   
    {
        'type':'agg',
        'name':'test_agg',
        'id':'B01',
        'hash':'00c7fffe403952167120afc0df7c164368fdfbb6f5ea0138bd96f6ff4bc5a8eb' #'tEst$A'
    },         
]


# databaseURL = ''
databaseURL = ''
appSecretKey = 'AlnConveyor$2021'
sessionTimeInMinutes = 600

#Moralis API key
moralisHeaders  = {
  'x-api-key': 'hDwiCzFEpHeNuHtHFReUBpdnat5IpX9fZBIvrVL3HX41muzsNsfXsKL8bB90TV8e'
}

EVMNetsOnMission = ['eth_main', 'rinkeby', 'bsc_main', 'bsc_test','polygon_main','avax_main','heco_main','hoo_main','ftm_main'] #all EVM nets allowed

RPC_links={
    'eth_main' : "https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    'rinkeby' : "https://rinkeby.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161",
    'bsc_main' : "https://bsc-dataseed.binance.org/",
    'bsc_test' : "https://data-seed-prebsc-1-s1.binance.org:8545/",
    'polygon_main':"https://rpc-mainnet.maticvigil.com",
    'heco_main':'https://http-mainnet-node.huobichain.com',
    'hoo_main':'https://http-mainnet.hoosmartchain.com',
    'ftm_main':'https://rpc.ftm.tools/',
    'avax_main': 'https://api.avax.network/ext/bc/C/rpc'
}

explorerDic = {
    'BTC':'https://blockchair.com/bitcoin/',
    'eth_main':'https://etherscan.io',
    'rinkeby':'https://rinkeby.etherscan.io',
    'bsc_main':'https://bscscan.com',
    'bsc_test':'https://testnet.bscscan.com',
    'polygon_main':'https://polygonscan.com',
    'hoo_main':'https://hooscan.com',
    'heco_main':'https://hecoinfo.com',
    'ftm_main':'https://ftmscan.com',
    'avax_main':'https://snowtrace.io/'
}

moralisNetMap = {
    'eth_main' : "eth",
    'rinkeby' : "rinkeby",
    'bsc_main' : "bsc",
    'bsc_test' : "testnet",
    'polygon_main':"polygon",
    'avax_main':'avalanche',
    'ftm_main':'fantom',
}

Blocktime={
    'eth_main' : 13.5,
    'rinkeby' : 15,
    'bsc_main' : 3,
    'bsc_test' : 3,
    'polygon_main' : 2.4,
    'heco_main':3,
    'hoo_main':3,
    'ftm_main':1,
    'avax_main':2
}

chainIdDict = {
    'eth_main': 1,
    'bsc_main': 56,
    'bsc_test':97,
    'rinkeby': 4,
    'polygon_main':137,
    'heco_main':128,
    'hoo_main':70,
    'ftm_main':250,
    'avax_main':43114
}

ContractAddresses = {
    'heco_main': [
        ['HBTC', '0x66a79d23e58475d2738179ca52cd0b41d73f0bea'], ['HETH', '0x64ff637fb478863b7468bc97d30a5bf3a428a1fd'], ['USDTHECO', '0xa71edc38d189767582c38a3145b5873052c3e47a'], ['HDOT', '0xa2c49cee16a5e5bdefde931107dc1fae9f7773e3'], ['USDC-HECO', '0x9362bbef4b8313a8aa9f0c9808b80577aa26b73b'], ['HUNI', '0x22c54ce8321a4015740ee1109d9cbc25815c46e6'], ['WBTC', '0x70d171d269d964d14af9617858540061e7be9ef1'], ['HLTC', '0xecb56cf772b5c9a6907fb7d32387da2fcbfb63b4'], ['LINK', '0x9e004545c59d359f6b7bfb06a26390b087717b42'], ['HBCH', '0xef3cebd77e0c52cb6f60875d9306397b5caca375'], ['HFIL', '0xae3a768f9ab104c69a7cd6041fe16ffa235d1810'], ['DAIHECKO', '0x3d760a45d0887dfd89a2f5385a236b29cb46ed2a'], ['HFTT', '0xc7f7a54892b78b5c812c58d9df8035fce9f4d445'], ['AAVE', '0x202b4936fe1a82a4965220860ae46d7d3939bb25'], ['TUSD', '0x5ee41ab6edd38cdfb9f6b4e6cf7f75c87e170d98'], ['HBAT', '0xb04ee982e6329febe4c70a53d1725469a1f6963a'], ['HMDX', '0x25d2e80cb6b86881fd7e07dd263fb79f4abe033c']
    ],
    'ftm_main':[
        ['fBTC', '0xe1146b9ac456fcbb60644c36fd3f868a9072fc6e'], ['fETH', '0x658b0c7613e890ee50b8c4bc6a3f41ef411208ad'], ['usd', '0x04068da6c83afcfa0e13ba15a6696662335d5b75'], ['BTC', '0x321162Cd933E2Be498Cd2267a90534A804051b11'], ['DAI', '0x8d11ec38a3eb5e956b052f67da8bdc9bef8abf3e'], ['WFTM', '0x21be370d5312f44cb42ce377bc9b8a0cef1a4c83'], ['MIM', '0x82f0b8b456c1a451378467398982d4834b6829c1'], ['YFI', '0x29b0Da86e484E1C0029B56e817912d778aC0EC69'], ['CRV', '0x1E4F97b9f9F913c46F1632781732927B9019C68b']
    ],
    'hoo_main':[
        []
    ],
    'rinkeby':[
        []
    ], 
    'bsc_test':[
        []
    ],        
}

ScammedAddresses={
    'eth_main':[
        '0x82dfDB2ec1aa6003Ed4aCBa663403D7c2127Ff67','0x34278F6f40079eae344cbaC61a764Bcf85AfC949','0x426CA1eA2406c07d75Db9585F22781c096e3d0E0','0xc92e74b131D7b1D46E60e07F3FaE5d8877Dd03F0','0x25677657E70694C79f64C3D477796aCb43A6f1c0','0x716523231368d43BDfe1F06AfE1C62930731aB13','0xe44061F043682ff77C1d51D4E0F93Ab2bb5b2ae0','0xf5E39300Ab38d19B777d507A2A52F86e0C0c51B0','0x21244db4d5A7477fe383139ced6df90e60Ed69b5','0x68e14bb5A45B9681327E16E528084B9d962C1a39','0xd73be539d6b2076bab83ca6ba62dfe189abc6bbe','0x86c8bF8532AA2601151c9DbbF4e4C4804e042571','0x85332b222787EacAb0fFf68cf3b884798823528C'
    ],
    'bsc_main':[
        '0x5190B01965b6E3d786706Fd4a999978626C19880','0xb16600c510b0f323dee2cb212924d90e58864421','0x373233a38ae21cf0c4f9de11570e7d5aa6824a1e','0x026222b0954457b5b12fa5fd8471238cf4e6749c','0xb926BEB62d7A680406E06327c87307C1FFC4aB09','0x0df62d2cd80591798721ddc93001afe868c367ff','0x89e0262ec34311564b4e43d416218d38d4db879c','0x36ab72472db0d5ca55a451d324b36a3230bf8674','0x585de5430f47aba099bebd21ef133272c38db7a6','0xd22202d23fe7de9e3dbe11a2a88f42f4cb9507cf','0x7269163f2b060fb90101f58cf724737a2759f0bb','0xf3822314b333cbd7a36753b77589afbe095df1ba','0x58ed15a338f179fd0fbbe951cee9de90d5bb29a0','0x575b0339a30d5f29dcbc444ab28f2b194a5e2fa7','0xC7Ef1bff46cD025509CF5e55FA5Cd5c14793CBFF','0x569b2cf0b745ef7fad04e8ae226251814b3395f9','0x8Ee3E98DCCeD9f5D3Df5287272f0b2d301D97C57','0xbC6675DE91e3DA8eAc51293ecb87c359019621CF','0x5558447b06867ffebd87dd63426d61c868c45904','0xc33fc11b55465045b3f1684bde4c0aa5c5f40124','0xab57aef3601cad382aa499a6ae2018a69aad9cf0','0x15351604e617d9f645b53ee211d9c95ba88297df','0x7d9c3bd1eb0b0a8921fab9c57e26e05518d87b4d','0x1882c296ebfa916a0ad194cfa0094c5e0086ba03','0xb8a9704d48c3e3817cc17bc6d350b00d7caaecf6','0x119e2ad8f0c85c6f61afdf0df69693028cdc10be','0x57dbae4b73455bc0d3e892ae57779160961f0f03','0x5E48C354a5Da2B0A8C203518d0fc7B9c58Cc9329','0x442b656f5a5c3dd09790951810c5a15ea5295b51'
    ],
    'polygon_main':[],
    'heco_main':[],
    'ftm_main':[],
    'hoo_main':[],
    'bsc_test':[],
    'rinkeby':[],
}
