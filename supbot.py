#! /usr/bin/env python
"""
An IRC bot. Lots of code taken from the irclib example bot.

Licence: GPLv2 (non-irclib bits) + LGPL (original bits from irclib)

Author: Joman Chu <supbot@notatypewriter.com>
Author: Peter Rowlands <peter@pmrowla.com>

Commands:
!sup - shows the last 100 lines of scrollback

"""


from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from collections import deque
import time


class SupBot(SingleServerIRCBot):
    """IRC Bot that provides scrollback"""

    def __init__(self, channel, nickname, server, port=6667, maxlen=100):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.suplist = deque()
        self.seenlist = {}
        self.maxlen = maxlen

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        msg = e.arguments()[0]
        if len(msg) > 0 and msg[0] == '!':
            self.do_command(e, msg.split(' '))

    def on_pubmsg(self, c, e):
        self.on_privmsg(c, e)

        timestamp = time.localtime()
        nick = nm_to_n(e.source())
        msg = e.arguments()[0]
        self.suplist.appendleft([nick, msg])
        if len(self.suplist) > self.maxlen:
            self.suplist.pop()
        # should possibly keep track of nick changes in the future
        self.seenlist[nick] = timestamp

    def do_command(self, e, cmdlist):
        cmd = cmdlist[0]
        arglist = cmdlist[1:]

        commands = {'!help': self.do_help,
                    '!sup': self.do_sup,
                    '!seen': self.do_seen}

        try:
            commands[cmd](e, arglist)
        except KeyError:
            # Unknown command
            pass

    def do_help(self, e, arglist):
        """Send a private msg with usage info"""
        conn = self.connection
        target = nm_to_n(e.source())
        conn.privmsg(target, 'This bot provides a few commands for users.')
        conn.privmsg(target, '!help - displays this message')
        conn.privmsg(target, '!sup [COUNT] - displays the last COUNT lines of scrollback. Defaults to COUNT=20.')
        conn.privmsg(target, '!seen NICK1 [NICK2]... - displays the last time each nick talked.')
        conn.privmsg(target, 'This bot is Open Source. Please contribute code at https://github.com/ENOTTY/supbot')

    def do_sup(self, e, arglist):
        """Print some lines of scrollback"""
        conn = self.connection
        i = 20
        if len(arglist) > 0:
            try:
                i = int(arglist[0])
            except ValueError:
                i = 20

        rev = self.suplist
        msgs = []
        for v in rev:
            msgs.append(v)
            i -= 1
            if i <= 0:
                break

        for [n,msg] in reversed(msgs):
            conn.privmsg(nm_to_n(e.source()), "%s: %s" % (n,msg))

    def do_seen(self, e, arglist):
        """Print the last time a user sent a message"""
        conn = self.connection
        msgs = []
        for nick in arglist:
            try:
                seen = self.seenlist[nick]
                msgs.append('%s: Last seen: %s %s' % (nick, time.asctime(seen), time.tzname[seen.tm_isdst]))
            except KeyError:
                msgs.append('%s: Last seen: never' % nick)
        for msg in msgs:
            conn.privmsg(nm_to_n(e.source()), msg)


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
