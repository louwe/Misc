import os
import telnetlib
import time
import subprocess
import re

def sshConn(host):
    retVal = ""
    sshCommands = 'enable\n term length 0\n show running-config\n term length 48 \n quit \n n'
    try:
        p = subprocess.Popen(['plink', '-ssh', '-l', 'admin', '-pw', '1qaz1qaz', host], \
            shell = False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        rawData, err = p.communicate(sshCommands.encode())
        retVal = rawData.decode()
    except:
        pass

    return retVal

def telnetConn(host):
    retVal = ""
    try:
        telnet = telnetlib.Telnet(host, timeout=10)
        telnet.read_until(b"User:")
        telnet.write(b"admin\n")
        telnet.read_until(b"Password:")
        telnet.write(b"1qaz1qaz\n")
        telnet.read_until(b">")
        telnet.write(b"enable \n")
        telnet.read_until(b"#")
        telnet.write(b"terminal length 0 \n")
        telnet.read_until(b"#")
        telnet.write(b"show running-config \n")
        telnet.read_until(b"\n")
        rawData = telnet.read_until(b"#")
        retVal = rawData.decode()
        telnet.write(b"terminal length 48 \n")
        telnet.read_until(b"#")
        telnet.write(b"quit\n")
        telnet.write(b"n\n")
        telnet.close()
    except:
        pass

    return retVal

def createFile(host, timestamp, cleanData):
    if(cleanData):
        if not os.path.exists(host):
            os.mkdir(host)
        os.chdir(host)
        file = open(host + "_" + timestamp + ".txt","w")
        file.write(cleanData)
        file.close()
        os.chdirir("../")
    else:
        file = open("ERROR_" + timestamp + ".txt","a+")
        file.write(host + "\n")
        file.close()

if __name__ == '__main__':
    timestamp = time.strftime("%Y%m%d")

    inFile = open("hosts.txt")
    inFileBuf = inFile.read()

    hostMatcher = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
    descriptionMatcher = re.compile(r"(?:\s*,\s*)(\w+[\w \t]*)(?:(?=\s+\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*)|\s+)")
    hostsList = hostMatcher.findall(inFileBuf)
    descriptionsList = descriptionMatcher.findall(inFileBuf)

    hostPairs = [[hostsList[i], descriptionsList[i]] for i in range(len(hostsList))]

    for hostPair in hostPairs:
        print(hostPair[0], ":", hostPair[1])
        cleanData = sshConn(hostPair[0])

        if(not cleanData):
            cleanData = telnetConn(hostPair[0])

        createFile(hostPair[0], timestamp, cleanData)
