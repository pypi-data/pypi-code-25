#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This file is free software by d0n <d0n@janeiskla.de>
#
# You can redistribute it and/or modify it under the terms of the GNU -
# Lesser General Public License as published by the Free Software Foundation
#
# This is distributed in the hope that it will be useful somehow.
# !WITHOUT ANY WARRANTY!
#
# Without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
"""pwclip main program"""
# global & stdlib imports
try:
	from os import fork
except ImportError:
	def fork(): """fork faker function""" ;return 0

from os import environ, path, remove, name as osname

from sys import argv

from subprocess import DEVNULL, Popen, call

from argparse import ArgumentParser

from argcomplete import autocomplete
from argcomplete.completers import FilesCompleter, ChoicesCompleter

from socket import gethostname as hostname

from time import sleep

from yaml import load

# local relative imports
from colortext import bgre, tabd, error, fatal

from system import copy, paste, xgetpass, xmsgok, xyesno, xnotify, which

# first if on windows and gpg.exe cannot be found in PATH install gpg4win
if osname == 'nt' and not which('gpg.exe'):
	if not xyesno('mandatory gpg4win not found! Install it?'):
		exit(1)
	import wget
	src = 'https://files.gpg4win.org/gpg4win-latest.exe'
	trg = path.join(environ['TEMP'], 'gpg4win.exe')
	wget.download(src, out=trg)
	try:
		call(trg)
	except TimeoutError:
		xmsgok('something went wrong while downloading gpg4win from: ' \
               'https://files.gpg4win.org/ - try installing yourself!')
		exit(1)
	finally:
		try:
			remove(trg)
		except FileNotFoundError:
			pass

from secrecy import PassCrypt, ykchalres, yubikeys

from pwclip.__pkginfo__ import version

def forkwaitclip(text, poclp, boclp, wait=3, out=None):
	"""clipboard forking, after time resetting function"""
	if out:
		if out == 'gui':
			Popen(str(
                'xvkbd -no-keypad -delay 10 -text %s'%text
                ).split(' '), stdout=DEVNULL, stderr=DEVNULL).communicate()
		else:
			print(text, end='')
	copy(text, mode='pb')
	if fork() == 0:
		try:
			sleep(int(wait))
		except (KeyboardInterrupt, RuntimeError):
			exit(1)
		finally:
			copy(poclp, mode='p')
			copy(boclp, mode='b')
		exit(0)

def __passreplace(pwlist):
	"""returnes a string of asterisk's as long as the password is"""
	__pwcom = ['*'*len(str(pwlist[0]))]
	if len(pwlist) > 1:
		__pwcom.append(pwlist[1])
	return __pwcom

def __dictreplace(pwdict):
	"""password => asterisk replacement function"""
	__pwdict = {}
	for (usr, ent) in pwdict.items():
		if isinstance(ent, dict):
			__pwdict[usr] = {}
			for (u, e) in ent.items():
				__pwdict[usr][u] = __passreplace(e)
		elif ent:
			__pwdict[usr] = __passreplace(ent)
	return __pwdict

def _printpws_(pwdict, insecure=False):
	"""password printer with in/secure option"""
	if not insecure:
		pwdict = __dictreplace(pwdict)
	print(tabd(pwdict))
	exit(0)

def confpars(mode):
	"""pwclip command line opt/arg parsing function"""
	_me = path.basename(path.dirname(__file__))
	cfg = path.expanduser('~/.config/%s.yaml'%_me)
	try:
		with open(cfg, 'r') as cfh:
			cfgs = load(cfh.read())
	except FileNotFoundError:
		cfgs = {}
	try:
		cfgs['time'] = environ['PWCLIPTIME']
	except KeyError:
		cfgs['time'] = 3 if 'time' not in cfgs.keys() else cfgs['time']
	try:
		cfgs['ykslot'] = environ['YKSLOT']
	except KeyError:
		cfgs['ykslot'] = None
	try:
		cfgs['ykser'] = environ['YKSERIAL']
	except KeyError:
		cfgs['ykser'] = None
	try:
		cfgs['binary']
	except KeyError:
		cfgs['binary'] = 'gpg2'
		if osname == 'nt':
			cfgs['binary'] = 'gpg'
	cfgs['user'] = '$USER' if osname != 'nt' else '$USERNAME'
	try:
		cfgs['user'] = environ['USER']
	except KeyError:
		cfgs['user'] = environ['USERNAME']
	if 'crypt' not in cfgs.keys():
		cfgs['crypt'] = path.expanduser('~/.passcrypt')
	elif 'crypt' in cfgs.keys() and cfgs['crypt'].startswith('~'):
		cfgs['crypt'] = path.expanduser(cfgs['crypt'])
	if 'plain' not in cfgs.keys():
		cfgs['plain'] = path.expanduser('~/.pwd.yaml')
	elif 'plain' in cfgs.keys() and cfgs['plain'].startswith('~'):
		cfgs['plain'] = path.expanduser(cfgs['plain'])
	desc = 'pwclip - Multi functional password manager to temporarily ' \
           'save passphrases to your copy/paste buffers for easy and ' \
           'secure accessing your passwords. Most of the following ' \
           'arguments mights also be set by the config ~/.config/%s.yaml'%_me
	epic = 'the yubikey feature is compatible with its\'s ' \
           'challenge-response feature only'
	pars = ArgumentParser(description=desc, epilog=epic)
	pars.set_defaults(**cfgs)
	pars.add_argument(
        '--version',
        action='version', version='%(prog)s-v'+version)
	pars.add_argument(
        '-D', '--debug',
        dest='dbg', action='store_true', help='debugging mode')
	pars.add_argument(
        '-A', '--all',
        dest='aal', action='store_true',
        help='switch to all users entrys ("%s" only is default)'%cfgs['user'])
	pars.add_argument(
        '-o', '--stdout',
        dest='out', action='store_const', const=mode,
        help='print password to stdout (insecure and unrecommended)')
	pars.add_argument(
        '-s', '--show-passwords',
        dest='sho', action='store_true',
        help='show passwords when listing (replaced by "*" is default)')
	pars.add_argument(
        '-t',
        dest='time', default=3, metavar='seconds', type=int,
        help='time to wait before resetting clip (%d is default)'%cfgs['time'])
	rpars = pars.add_argument_group('remote arguments')
	rpars.add_argument(
        '-R',
        dest='rem', action='store_true',
        help='use remote backup given by --remote-host')
	rpars.add_argument(
        '--remote-host',
        dest='rehost', metavar='HOST',
        help='use HOST for connections')
	rpars.add_argument(
        '--remote-user',
        dest='reuser', metavar='USER',
        help='use USER for connections to HOST ("%s" is default)'%cfgs['user'])
	gpars = pars.add_argument_group('gpg/ssl arguments')
	gpars.add_argument(
        '-r', '--recipients',
        dest='rcp', metavar='"ID ..."',
        help='one ore more gpg-key ID(s) to use for ' \
             'encryption (strings seperated by spaces within "")')
	gpars.add_argument(
        '-u', '--user',
        dest='usr', metavar='USER', default=cfgs['user'],
        help='query entrys only for USER (-A overrides, ' \
             '"%s" is default)'%cfgs['user'])
	pars.add_argument(
        '-p', '--password',
        dest='pwd', default=None,
        help='enter password for add/change actions' \
             '(insecure & not recommended)')
	pars.add_argument(
        '--comment',
        dest='com', default=None,
        help='enter comment for add/change actions')
	gpars.add_argument(
        '-x', '--x509',
        dest='gpv', action='store_const', const='gpgsm',
        help='force ssl compatible gpgsm mode - usually is autodetected ' \
             '(use --cert & --key for imports)')
	gpars.add_argument(
        '-C', '--cert',
        dest='sslcrt', metavar='SSL-Certificate',
        help='one-shot setting of SSL-Certificate')
	gpars.add_argument(
        '-K', '--key',
        dest='sslkey', metavar='SSL-Private-Key',
        help='one-shot setting of SSL-Private-Key')
	gpars.add_argument(
        '--ca', '--ca-cert',
        dest='sslca', metavar='SSL-CA-Certificate',
        help='one-shot setting of SSL-CA-Certificate')
	gpars.add_argument(
        '-P', '--passcrypt',
        dest='pcr', metavar='CRYPTFILE',
        default=path.expanduser('~/.passcrypt'),
        help='set location of CRYPTFILE to use as ' \
             'password store (~/.passcrypt is default)')
	gpars.add_argument(
        '-Y', '--yaml',
        dest='yml', metavar='YAMLFILE',
        default=path.expanduser('~/.pwd.yaml'),
        help='set location of YAMLFILE to read whole ' \
             'sets of passwords from a yaml file (~/.pwd.yaml is default)')
	gpars.add_argument(
        '-S', '--slot',
        dest='ysl', default=None, type=int, choices=(1, 2),
        help='set one of the two yubikey slots (only useful with -y)'
        ).completer = ChoicesCompleter((1, 2))
	ypars = pars.add_argument_group('yubikey arguments')
	ypars.add_argument(
        '-y', '--ykserial',
        nargs='?', dest='yks', metavar='SERIAL', default=False,
        help='switch to yubikey mode and optionally set ' \
		     'SERIAL of yubikey (autoselect serial and slot is default)')
	gpars = pars.add_argument_group('action arguments')
	gpars.add_argument(
        '-a', '--add',
        dest='add', metavar='ENTRY',
        help='add ENTRY (password will be asked interactivly)')
	gpars.add_argument(
        '-c', '--change',
        dest='chg', metavar='ENTRY',
        help='change ENTRY (password will be asked interactivly)')
	gpars.add_argument(
        '-d', '--delete',
        dest='rms', metavar='ENTRY', nargs='+',
        help='delete ENTRY(s) from the passcrypt list')
	gpars.add_argument(
        '-l', '--list',
        nargs='?', dest='lst', metavar='PATTERN', default=False,
        help='pwclip an entry matching PATTERN if given ' \
             '- otherwise list all entrys')
	autocomplete(pars)
	args = pars.parse_args()
	pargs = [a for a in [
        'aal' if args.aal else None,
        'dbg' if args.dbg else None,
        'gsm' if args.gpv else None,
        'rem' if args.sho else None,
        'sho' if args.sho else None] if a]
	__bin = 'gpg2'
	if args.gpv:
		__bin = args.gpv
	if osname == 'nt':
		__bin = 'gpgsm.exe' if args.gpv else 'gpg.exe'
	pkwargs = {}
	pkwargs['binary'] = __bin
	pkwargs['sslcrt'] = args.sslcrt
	pkwargs['sslkey'] = args.sslkey
	if args.pcr:
		pkwargs['crypt'] = args.pcr
	if args.rcp:
		pkwargs['recvs'] = list(args.rcp.split(' '))
	if args.usr:
		pkwargs['user'] = args.usr
	if args.time:
		pkwargs['time'] = args.time
	if args.yml:
		pkwargs['plain'] = args.yml
	if hasattr(args, 'remote'):
		pkwargs['remote'] = args.remote
	if hasattr(args, 'reuser'):
		pkwargs['reuser'] = args.reuser
	if args.dbg:
		print(bgre(pars))
		print(bgre(tabd(args.__dict__, 2)))
		print(bgre(pkwargs))
	if mode == 'gui':
		return args, pargs, pkwargs
	#print(tabd(args.__dict__))
	if (
          args.yks is False and args.lst is False and \
          args.add is None and args.chg is None and \
          args.rms is None and (args.sslcrt is None and args.sslkey is None)):
		pars.print_help()
		exit(1)
	return args, pargs, pkwargs

def cli():
	args, pargs, pkwargs = confpars('cli')
	if not path.isfile(args.yml) and \
          not path.isfile(args.pcr) and args.yks is False:
		with open(args.yml, 'w+') as yfh:
			yfh.write("""---\n%s:  {}"""%args.usr)
	poclp, boclp = paste('pb')
	if args.yks or args.yks is None:
		if 'YKSERIAL' in environ.keys():
			__ykser = environ['YKSERIAL']
		__ykser = args.yks if args.yks and len(args.yks) >= 6 else None
		__in = xgetpass()
		__res = ykchalres(__in, args.ysl, __ykser)
		if not __res:
			fatal('could not get valid response on slot ', args.ysl)
		forkwaitclip(__res, poclp, boclp, args.time)
		exit(0)
	__ents = None
	if args.add:
		if not PassCrypt(*pargs, **pkwargs).adpw(args.add, args.pwd, args.com):
			fatal('could not add entry ', args.add)
	elif args.chg:
		if args.pwd:
			pkwargs['password'] = args.pwd
		if not PassCrypt(*pargs, **pkwargs).chpw(args.chg, args.pwd, args.com):
			fatal('could not change entry ', args.chg)
	elif args.rms:
		for r in args.rms:
			if not PassCrypt(*pargs, **pkwargs).rmpw(r):
				error('could not delete entry ', r)
	elif args.lst is not False:
		__ents = PassCrypt(*pargs, **pkwargs).lspw(args.lst)
		if not __ents:
			fatal('could not decrypt')
		elif __ents and args.lst and not args.lst in __ents.keys():
			fatal(
                'could not find entry for ',
                args.lst, ' in ', pkwargs['crypt'])
		elif args.lst and __ents:
			__pc = __ents[args.lst]
			if __pc:
				if len(__pc) == 2:
					xnotify('%s: %s'%(
                        args.lst, ' '.join(__pc[1:])), args.time)
				forkwaitclip(__pc[0], poclp, boclp, args.time, args.out)
	if not __ents:
		__ents = PassCrypt(*pargs, **pkwargs).lspw()
	_printpws_(__ents, args.sho)

def gui(typ='pw'):
	"""gui wrapper function to not run unnecessary code"""
	poclp, boclp = paste('pb')
	args, pargs, pkwargs = confpars('gui')
	if typ == 'yk':
		__in = xgetpass()
		__res = ykchalres(__in, args.ykslot, args.ykser)
		if not __res:
			xmsgok('no entry found for %s or decryption failed'%__in)
			exit(1)
		forkwaitclip(__res, poclp, boclp, args.time)
		exit(0)
	pcm = PassCrypt(*pargs, **pkwargs)
	while True:
		__in = xgetpass()
		if not __in: exit(1)
		__ent = pcm.lspw(__in)
		if __ent and __in:
			if __in not in __ent.keys() or not __ent[__in]:
				xmsgok('no entry found for %s'%__in)
				if xyesno('try again?'):
					continue
				exit(1)
			__pc = __ent[__in]
			if __pc:
				if len(__pc) == 2:
					xnotify('%s: %s'%(__in, ' '.join(__pc[1:])), args.time)
				forkwaitclip(__pc[0], poclp, boclp, args.time, args.out)
				exit(0)
	exit(0)



if __name__ == '__main__':
	exit(1)
