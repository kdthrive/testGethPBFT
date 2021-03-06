#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import requests
import json
from ips import IPList
from time import sleep

class GethNode():
    '''
    Data structure for Geth-pbft client.
    '''
        #n = GethNode(IPlist, 0, 1, 121)
    def __init__(self, IPlist, pbftid, nodeindex, blockchainid, passwd='Blockchain17'):
        self.Enode = ''
        self._id = nodeindex
        self._ip, self._rpcPort, self._listenerPort = IPlist.getNewPort()
        self._pbftid = pbftid
        self._nodeindex = nodeindex
        self._blockchainid = blockchainid
        self._name = 'geth-pbft' + str(self._rpcPort)
        self._headers = {'Content-Type': 'application/json'}
        self._passwd = passwd

    def start(self):
        '''
        Start a geth-pbft node on remote server.
        '''

        RUN_DOCKER = ('docker run -d -p %d:8545 -p %d:30303 --rm --name %s rkdghd/geth-pbft --rpcapi admin,eth,miner,web3,'
                      'net,personal --rpc --rpcaddr \"0.0.0.0\" --datadir /root/abc --pbftid %d --nodeindex %d '
                      '--blockchainid %d --syncmode \"full\" ') % (self._rpcPort, self._listenerPort, self._name,
                                                                    self._pbftid, self._nodeindex, self._blockchainid)
#        print(RUN_DOCKER)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self._ip, port=22, username='root', password=self._passwd)
        try:
            stdin, stdout, stderr = ssh.exec_command(RUN_DOCKER)
            err = stderr.read().strip()
            out = stdout.read().strip()

            if not err and out:
#                print(stdout.read().strip().decode(encoding='utf-8'))
                print('node %s of blockchain %s at %s:%s started' % (self._nodeindex, self._blockchainid, self._ip, self._rpcPort))
                sleep(3)
                msg = self.__msg("admin_nodeInfo", [])
                url = "http://{}:{}".format(self._ip, self._rpcPort)
                try:
                    response = requests.post(url, headers=self._headers, data=msg)
                    enode = json.loads(response.content.decode(encoding='utf-8'))['result']['enode'].split('@')[0]
                    self.Enode = '{}@{}:{}'.format(enode, self._ip, self._listenerPort)
                    print(self.Enode)
                except Exception as e:
                    print("getEnode", e)
            else:
                print('%s@%s' % (self._ip, self._listenerPort), err, "start step")
            # result = stdout.read()
            # print(result)
        except Exception as e:
            print(e)
        ssh.close()

    def __msg(self, method, params):
        '''
        Return json string used in HTTP requests.
        '''
        return json.dumps({
               "jsonrpc": "2.0",
               "method": method,
               "params": params,
               "id": self._id
               })

    def getEnode(self):
        '''
        Return enode information from admin.nodeInfo.
        '''
        return self.Enode

    def getPeerCount(self):
        '''
        net.peerCount
        '''
        sleep(0.5)
        msg = self.__msg("net_peerCount", [])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            count = int(json.loads(response.content.decode(encoding='utf-8'))['result'], 16)
            return count
        except Exception as e:
            print("getPeerCount", e)

    def getPeers(self):
        '''
        admin.peers
        '''
        sleep(0.5)
        msg = self.__msg("admin_peers", [])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            peers = json.loads(response.content.decode(encoding='utf-8'))['result']
            return peers
        except Exception as e:
            print("getPeers", e)

    def newAccount(self, password='root'):
        '''
        personal.newAccount(password)
        '''
        sleep(0.5)
        msg = self.__msg("personal_newAccount", [password])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))['result']
            return result
        except Exception as e:
            print("newAccount", e)

    def unlockAccount(self, account, password='root', duration=86400):
        '''
        personal.unlockAccount()
        '''
        sleep(0.5)
        msg = self.__msg("personal_unlockAccount", [account, password, duration])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))['result']
            return result
        except Exception as e:
            print("unlockAccount", e)

    def sendTransaction(self, toID, toIndex, value):
        '''
        eth.sendTransaction2()
        '''
        if isinstance(value, int):
            value = hex(value)
        param = {"toid":toID, "toindex":toIndex, "value":value}
        msg = self.__msg("eth_sendTransaction2", [param])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))['result']
            return result
        except Exception as e:
            print("sendTransaction", e)

    def send1000Transaction(self, toID, toIndex, value):
        '''
        eth.testSendTransaction2()
        '''
        if isinstance(value, int):
            value = hex(value)
        param = {"toid":toID, "toindex":toIndex, "value":value}
        msg = self.__msg("eth_testSendTransaction2", [param])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))['result']
            return result
        except Exception as e:
            print("send1000Transaction", e)

    def getTransaction(self, TXID):
        '''
        eth.getTransaction()
        '''
        msg = self.__msg("eth_getTransaction", [TXID])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))['result']
            return result
        except Exception as e:
            print("result", e)

    def getAccounts(self):
        '''
        eth.accounts
        '''
        sleep(0.5)
        msg = self.__msg("eth_accounts", [])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            accounts = json.loads(response.content.decode(encoding='utf-8'))['result']
            return accounts
        except Exception as e:
            print("getAccounts", e)

    def getBalance(self, account):
        '''
        eth.getBalance()
        '''
        msg = self.__msg("eth_getBalance", [account])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            balance = json.loads(response.content.decode(encoding='utf-8'))['result']
            return balance
        except Exception as e:
            print("getBalance", e)


    def addPeer(self, *param):
        '''
        admin.addPeer()
        '''
        sleep(0.3)
        msg = self.__msg("admin_addPeer", param)
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            info = requests.post(url, headers=self._headers, data=msg)
            print(info.json())
            sleep(0.5)
            # print(response.content)
        except Exception as e:
            print("addPeer", e)

    def setNumber(self, n, t):
        '''
        admin.setNumber()
        '''
        if n < t:
            raise ValueError("nodeCount should be no less than threshold value")
        sleep(2)
        msg = self.__msg("admin_setNumber", [n, t])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))
            print("node at %s:%d setNumber result: %s" % (self._ip, self._listenerPort, result["result"]))
        except Exception as e:
            print("setNumber", e)

    def setLevel(self, level, maxLevel):
        '''
        admin.setLevel()
        '''
        if maxLevel < level:
            raise ValueError("level should be no larger than maxLevel")
        sleep(2)
        msg = self.__msg("admin_setLevel", [maxLevel, level])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))
            print("node at %s:%d setLevel result: %s" % (self._ip, self._listenerPort, result["result"]))
        except Exception as e:
            print("setLevel", e)

    def setID(self, id):
        '''
        admin.setID()
        '''
        sleep(2)
        msg = self.__msg("admin_setID", ['%d'.format(id)])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            result = json.loads(response.content.decode(encoding='utf-8'))
            print("node at %s:%d setID result: %s" % (self._ip, self._listenerPort, result["result"]))
        except Exception as e:
            print("setID", e)

    def testHIBE(self, txString):
        '''
        admin.testhibe()
        '''
        sleep(2)
        msg = self.__msg("admin_testhibe", ['%d'.format(txString)])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            print(response.content)
        except Exception as e:
            print("testHIBE", e)

    def isRunning(self):
        '''
        Check if the client is running.
        '''
        sleep(0.5)
        msg = self.__msg("admin_nodeInfo", [])
        url = "http://{}:{}".format(self._ip, self._rpcPort)
        try:
            response = requests.post(url, headers=self._headers, data=msg)
            return True if response else False
        except Exception as e:
            print("isRunning", e)

    def stop(self):
        '''
        Remove the geth-pbft node container on remote server.
        '''
        sleep(0.5)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=self._ip, port=22, username='root', password=self._passwd)
        STOP_CONTAINER = "docker stop %s" % self._name
        try:
            stdin, stdout, stderr = ssh.exec_command(STOP_CONTAINER)
            result = stdout.read()
            if result:
                print('node %s of blockchain %s at %s:%s stopped' % (self._nodeindex, self._blockchainid, self._ip, self._listenerPort))
            elif not stderr:
                print('%s@%s' % (self._ip, self._listenerPort), stderr, "stop step")
            return True if result else False
        except Exception as e:
            print("stop", e)
        ssh.close()

def execCommand(cmd, ip, port=22, username='root', password='Blockchain17'):
    '''
    exec a command on remote server using SSH
    '''
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, username, password)
    stdin, stdout, stderr = client.exec_command(cmd)
    if not stderr.read():
        result = stdout.read().strip().decode(encoding='utf-8')
    else:
        result = stderr.read().strip().decode(encoding='utf-8')
    return result

def stopAll(IP, passwd='Blockchain17'):
    '''
    stop all running containers on remote server
    '''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=IP, port=22, username='root', password=passwd)
    try:
        NAMES = "docker ps --format '{{.Names}}'"
        stdin, stdout, stderr = ssh.exec_command(NAMES)
        result = stdout.read()
        if result:
            result = result.decode(encoding='utf-8', errors='strict').split()
            print(' '.join(result))
            STOP = 'docker stop %s' % ' '.join(result)
            stdin, stdout, stderr = ssh.exec_command(STOP)
            result = stdout.read()
            if result:
                print("all nodes at %s have stopped" % IP)
            elif not stderr:
                print(stderr)
#            return True if result else False
        elif not stderr:
            print(stderr)
    except Exception as e:
        print('stopAll', e)
    ssh.close()

if __name__ == "__main__":
    IPlist = IPList('ip.txt')
    n = GethNode(IPlist, 0, 1, 121)
    n.start()
    enode = n.Enode
    print(enode)
    passwd = "root"
    print(n.newAccount(passwd))
    print(n.getAccounts())
    n.stop()
    stopAll(n._ip)