# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 <kang@insecure.ws>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This script name is inspired by Gavin Sharp's IRSSI script: rememberpass.pl
# Available at https://people.mozilla.org/~gavin/irssi/scripts/rememberpass.pl
#
# History
#
# Version 1.0 2013-10-03:
# 	First version of this terrible hack ;-)

import weechat as w

SCRIPT_NAME    = "rememberpass"
SCRIPT_AUTHOR  = "<kang@insecure.ws>"
SCRIPT_VERSION = "1.0"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC    = "Saves to disk IRC channel password/key when changed"

def save_channel_key(server, channel, key):
	"""Parse and save the horrible weechat channel/key format"""
	cfg_path = "irc.server.%s.autojoin" % (server)
	old_cfg = w.config_string(w.config_get(cfg_path))

	old_cfg_s = old_cfg.split(" ")
	try:
		chans = old_cfg_s[0].split(",")
	except IndexError:
		chans = []
	try:
		keys = old_cfg_s[1].split(",")
	except IndexError:
		keys = []

# If channel wasn't saved previously, we don't save it now either
	if channel not in chans:
		return

	i = -1
	for c in chans:
		i += 1
		if c == channel:
			break
	
# Channel didn't have a key before and is the only channel in the list.
# Due to the horrible format, all channels actually have a key so this only may happen
# in the aforementionned case.
	if len(keys) -1 < i:
		keys.append(key)
	else:
		keys[i] = key
	new_cfg = ','.join(chans)+' '+','.join(keys)

# Not sure how to call config_write and config_new *properly*, so hacking around...
	w.command("", "/set %s %s" % (cfg_path, new_cfg))
	w.command("", "/save irc")

def modifier_cb(data, modifier, modifier_data, string):
	try:
		modes = string.split("MODE")[1].split(" ")
		channel = modes[1]
		modes = modes[2:]
	except:
		return "%s %s" % (string, modifier_data)

# Some sanity checks...
# No channel, bail out
	if not channel.startswith('#'):
		return "%s %s" % (string, modifier_data)
# Not +k, bail out
	if modes[0].find('k') == -1:
		return "%s %s" % (string, modifier_data)
# Empty key, bail out
	if len(modes) != 2:
		return "%s %s" % (string, modifier_data)

	save_channel_key(modifier_data, channel, modes[1])

	return "%s %s" % (string, modifier_data)

if w.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION, SCRIPT_LICENSE, SCRIPT_DESC, "", ""):
	w.hook_modifier("irc_in_mode", "modifier_cb", "")
else:
	w.prnt("", "failed to load rememberpass")
