import datetime
import formatter
import re

class stdout(object): 
    def __init__(self, msg):
        self.msg = msg
        if self.msg.split(" ")[0] != "PING":
            fmt = formatter.formatter(msg)
            self.nick = fmt.nick()
            self.userwithip = fmt.userwithip()
            self.status = fmt.status()
            self.channel = fmt.channel()
            self.fmt = fmt
            self.date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            pass
            

    def standard(self):
        if self.msg.split(" ")[0] == "PING":
            return "[PING] " + re.match(r'^PING\s:(.+)$', self.msg).group(1)
        elif self.status == "PRIVMSG":
            return "[%s][%s][%s (%s)][%s] %s" % (self.date, self.channel, self.nick, self.userwithip, self.status, self.fmt.msgdetail())
        else:
            return "[%s][%s][%s (%s)][%s]" % (self.date, self.channel, self.nick, self.userwithip, self.status)

    def nodate(self):
        if self.msg.split(" ")[0] == "PING":
            return "[PING] " + re.match(r'^PING\s:(.+)$', self.msg).group(1)
        elif self.status == "PRIVMSG":
            return "[%s][%s (%s)][%s] %s" % (self.channel, self.nick, self.userwithip, self.status, self.fmt.msgdetail())
        else:
            return "[%s][%s (%s)][%s]" % (self.channel, self.nick, self.userwithip, self.status)

    def nouserwithip(self):
        if self.msg.split(" ")[0] == "PING":
            return "[PING] " + re.match(r'^PING\s:(.+)$', self.msg).group(1)
        elif self.status == "PRIVMSG":
            return "[%s][%s][%s][%s] %s" % (self.date, self.channel, self.nick, self.status, self.fmt.msgdetail())
        else:
            return "[%s][%s][%s][%s]" % (self.date, self.channel, self.nick, self.status)

    def custom(self, args):
        strout = ""
        for i in range(len(args)):
                strout = strout + "[" + args[i] + "]"

        if self.msg.split(" ")[0] == "PING":
            return "[PING] " + re.match(r'^PING\s:(.+)$', self.msg).group(1)
        elif self.status == "PRIVMSG":
            return strout + " " + self.fmt.msgdetail
        else:
            return strout
