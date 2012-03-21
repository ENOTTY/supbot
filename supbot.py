#! /usr/bin/env python
#
# An IRC bot. Lots of code taken from the irclib example bot.
#
# Licence: GPLv2 (non-irclib bits) + LGPL (original bits from irclib)
#
# Joman Chu <supbot@notatypewriter.com>

"""
!sup - shows the last 100 lines of scrollback
"""

from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from collections import deque

class SupBot(SingleServerIRCBot):

    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.suplist = deque(maxlen=100)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.on_pubmsg(c, e)

    def on_pubmsg(self, c, e):
        msg = e.arguments()[0]
        if len(msg) > 0 and msg[0] == '!':
            self.do_command(e, msg.split(' '))

        nick = nm_to_n(e.source())
        self.suplist.append([nick, msg])

        return

    def do_command(self, e, cmdlist):
        cmd = cmdlist[0]
        arglist = cmdlist[1:]
        conn = self.connection

        if cmd == '!sup':
            for [n,msg] in self.suplist:
                conn.privmsg(nm_to_n(e.source()), "%s: %s" % (n,msg))

def main():
    import sys
    if len(sys.argv) != 4:
        print "Usage: supbot <server[:port]> <channel> <nickname>"
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print "Error: Erroneous port."
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = SupBot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
