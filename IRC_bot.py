import socket
import re
import threading
import time
import sys
import os
import Queue
import subprocess

if os.name == 'nt':
    import winsound

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

queue = Queue.Queue()


def alert():
    if os.name == 'nt':
        for i in range(2):
            winsound.Beep(3000, 150)
    else:
        print '/a'
        print '/a'


def join(channel):
    irc.send("JOIN " + channel + "\n")


def ping(irc, msg):
    time.sleep(10)
    irc.send("PONG :" + msg.strip("PING :") + "\n")


def send_msg(destination, msg):
    irc.send("PRIVMSG " + destination + " :" + msg + "\n")


def add_db(s):
    db = open('db.txt', 'r')
    cond = db.read()
    db.close()
    db = open('db.txt', 'a+')
    if cond == '':
        db.write('%s' % s)
        db.close()
    else:
        db.write('|%s' % s)
        db.close()


def show_db():
    db = open('db.txt', 'r+')
    data = db.read()
    db.close()
    if data == '':
        send_msg(user_nick, 'Database empty!')
    else:
        send_msg(user_nick, '%s' % data)


def remove_db():
    db = open('db.txt', 'r+')
    db.truncate()
    db.close()


class inspect_thread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop = False
        self.queue = queue

    def run(self):
        while True:
            inf = queue.get()
            db = open('db.txt', 'r+')
            data = db.read()
            db.close()
            if re.findall(data, inf) != []:
                alert()
                log = open('log.txt', 'a+')
                log.write("[!]" + inf + "\n\r")
            if self.stop:
                send_msg(user_nick, '[*] Inspect process stopped!')
                break

def irc_command(irc, msg):
    irc.send("%s \n" % msg[msg.find('irc '):].strip('irc '))


def self_command(irc, msg):
    command = msg[msg.find('exec '):].strip('exec ')
    exec (command, {"__builtins__": None}, {'add_db': add_db, 'show_db': show_db, 'remove_db': remove_db})


def authen(irc, irc_msg):
    user_nick = irc_msg[1:irc_msg.find('!')]
    send_msg(user_nick, 'Who are you ?')
    irc_msg = irc.recv(2048)

    if irc_msg.find("PING") != -1:
        ping(irc, irc_msg)
        irc_msg = irc.recv(2048)

    elif hash((irc_msg[(irc_msg[1:].find(':') + 2):]).strip("\n\r")) == -1730159820:
        send_msg(user_nick, 'Please enter password: ([!!] Caution: Raw text !)')
        irc_msg = irc.recv(2048)
        if hash((irc_msg[(irc_msg[1:].find(':') + 2):]).strip("\n\r")) == -688607386:
            send_msg(user_nick, 'Waiting for your command, master! ')
            return (True, user_nick)
        else:
            send_msg(user_nick, 'Wrong password!! Authentication failed!, please do it again!')
            return (False, user_nick)
    else:
        send_msg(user_nick, 'Who the hell are you? Go away!')
        return (False, user_nick)


def run_command(command):
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
        send_msg(user_nick, "[*] Command executed successfully!")
    except:
        send_msg(user_nick, "[!] False to execute command!")


def main():
    global auth
    global user_nick
    ins = inspect_thread()

    host = raw_input("Server? ")
    port = raw_input("Port? (6667)")
    channel = raw_input("Channel? ")

    if port == "":
        port = 6667
    else:
        port = int(port)

    bot_nick = "cribot"
    user_nick = ""

    irc.connect((host, port))
    irc.send("USER " + bot_nick + " " + bot_nick + " " + bot_nick + " :death_bot\n")
    irc.send("NICK %s \n" % bot_nick)
    join(channel)

    while True:
        irc_msg = irc.recv(2048)
        irc_msg = irc_msg.strip("\n\r")
        queue.put(irc_msg)
        print irc_msg

        if irc_msg.find("PING") != -1:
            ping(irc, irc_msg)

        if irc_msg.find('PRIVMSG %s :authen' % bot_nick) != -1:
            (auth, user_nick) = authen(irc, irc_msg)

        if irc_msg.find('PRIVMSG %s :irc ' % bot_nick) != -1:
            if auth:
                irc_command(irc, irc_msg)
            else:
                send_msg(user_nick, 'I can\'t understand what you say!')

        if irc_msg.find('PRIVMSG %s :exec ' % bot_nick) != -1:
            if auth:
                self_command(irc, irc_msg)
            else:
                send_msg(user_nick, 'I can\'t understand what you say!')

        if irc_msg.find('inspect --start') != -1:
            if auth:
                ins.start()
                send_msg(user_nick, '[*] Inspect process started!')
            else:
                send_msg(user_nick, 'I can\'t understand what you say!')

        if irc_msg.find('inspect --stop') != -1:
            if auth:
                ins.stop = True
                del ins
            else:
                send_msg(user_nick, 'I can\'t understand what you say!')

        if irc_msg.find('cli ') != -1:
            if auth:
                command = irc_msg[irc_msg.find('cli ') + 4:]
                run_command(command)
            else:
                send_msg(user_nick, 'I can\'t understand what you say!')

        if irc_msg == '':
            sys.exit()


main()
