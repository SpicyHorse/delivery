from types import StringType, UnicodeType, IntType, LongType, DictType, ListType, TupleType, BooleanType

from hashlib import sha1
from time import time
import os

__all__ = [ "Metainfo", "bencode" ]

class Metainfo(dict):
	def __init__(self, filename, announce=None, nodes=None, httpseeds=None,
				 url_list=None, comment=None, piece_length=256*1024,
				 private=False, merkle=False):
		"""Create a BitTorrent metainfo structure (cf. BEP-3).

		Positional arguments:
		filename -- name of the file or directory to be distributed

		Keyword arguments:
		announce	 -- list of list of tracker announce URL, in the format
						[["main1", "main2", ...], ["backup1", "backup2", ...], ...]
						(cf. BEP-12)
		nodes		 -- list of DHT nodes, in the format [["host", port], ...]
						(cf. BEP-5)
		httpseeds	 -- list of HTTP seed URLs, in the format ["url", "url", ...]
						(cf. BEP-17)
		url_list	 -- list of HTTP/FTP seeding URLs (GetRight style), in the
						format ["url", "url", ...] (cf. BEP-19)
		comment		 -- optional comment
		piece_length -- lenght (in bytes) of the pieces into which the file(s)
						will be split (defaults to 256 kibi, cf. BEP-3)
		private		 -- forbid DHT and peer exchange (optional, defaults to False,
						cf. BEP-27)
		merkle		 -- generate a Merkle torrent (defaults to False, cf. BEP-30)

		Return: a dictionary-like structure, ready to be bencoded

		Notes:
		* You should provide either an announce list of liste, or a nodes list.
		* All strings given should be bytes, not str.

		"""
		if announce:
			self["announce"] = announce[0][0]
			if len(announce[0]) > 1 or len(announce) > 1 :
				self["announce-list"] = announce
		self.announce = announce
		if nodes:
			self["nodes"] = nodes
		self.nodes = nodes
		if httpseeds:
			self["httpseeds"] = httpseeds
		self.httpseeds = httpseeds
		if url_list:
			self["url-list"] = url_list
		self.url_list = url_list
		self["creation date"] = int(time())
		if comment:
			self["comment"] = comment
		self["created by"] = "SpicyDelivery".encode('utf-8')
		# Now we build the info dictionnary
		self["info"] = {}
		info = self["info"]
		info["piece length"] = piece_length
		pieces = bytearray()
		if private:
			info["private"] = 1
		info["name"] = os.path.basename(os.path.normpath(filename))
		if os.path.isfile(filename):
			info["length"] = os.path.getsize(filename)
			with open(filename, mode='rb') as f:
				while True:
					chunk = f.read(piece_length)
					if len(chunk) == 0:
						# We exactly reached the end at last iteration
						break
					pieces.extend(sha1(str(chunk)).digest())
					if len(chunk) < piece_length:
						# We have reached the end
						break
		elif os.path.isdir(filename):
			dirname = filename
			info["files"] = []
			files = info["files"]
			incomplete_chunk = bytearray()
			for dirpath, dirnames, filenames in os.walk(dirname):
				for filename in filenames:
					filedict = {}
					filename = os.path.join(dirpath, filename)
					filedict["path"] = os.path.relpath(filename, dirname).split(os.sep.encode('ascii'))
					filedict["length"] = os.path.getsize(filename)
					with open(filename, mode='rb') as f:
						while True:
							chunk = f.read(piece_length - len(incomplete_chunk))
							if len(chunk) == 0:
								# We exactly reached the end at last iteration
								break
							if len(incomplete_chunk) + len(chunk) < piece_length:
								# We have reached the end and got an incomplete chunk
								incomplete_chunk += chunk
								break
							# We have got a complete chunk
							pieces.extend(sha1(str(incomplete_chunk + chunk)).digest())
							incomplete_chunk = bytearray()
					files.append(filedict)
			if incomplete_chunk:
				# We have an incomplete chunk left to hash
				pieces.extend(sha1(str(incomplete_chunk)).digest())
		if merkle:
			# Merkle torrent: we calculate the Merkle tree's root node
			# to use in in place of the pieces.
			padding = 20 * "\0"
			# Reduce the hashes until there is only one left
			# (hashes are 20 bytes long).
			while len(pieces) > 20:
				if len(pieces) % 40:
					# There is an odd number of pieces: we padd it with
					# zeros... or recursive hashes of zeros as we are
					# clibing the tree, cf. BEP-30.
					pieces.extend(padding)
				# Hash the hashes by two and store the result in place
				for i in range(0, len(pieces) // 2, 20):
					pieces[i:i + 20] = sha1(str(pieces[2*i:2*i + 40])).digest()
				# Next level...
				# Truncate the hash list as all our new pieces are now only
				# in its first half.
				del pieces[len(pieces)//2:]
				# The padding at the new level is the result of hashing two
				# padding pieces together, cf. BEP-30.
				padding = sha1(str(2 * padding)).digest()
			info["root hash"] = pieces
		else:
			# Regular torrent: we use the pieces directly
			info["pieces"] = pieces
		# Shortcuts
		self.info = info
		self.__infohash = None
		self.name = info["name"]
		if "length" in info :
			self.length = info["length"]
		else :
			self.length = None

	@property
	def infohash(self):
		if not self.__infohash:
			self.__infohash = sha1(bencode(self.info)).hexdigest()
		return self.__infohash

def encode_int(x, r):
	r.extend(('i', str(x), 'e'))

def encode_bool(x, r):
	if x:
		encode_int(1, r)
	else:
		encode_int(0, r)
		
def encode_string(x, r):
	r.extend((str(len(x)), ':', x))

def encode_unicode(x, r):
	r.extend((str(len(x)), ':', str(x)))

def encode_list(x, r):
	r.append('l')
	for i in x:
		encode_func[type(i)](i, r)
	r.append('e')

def encode_dict(x,r):
	r.append('d')
	ilist = x.items()
	ilist.sort()
	for k, v in ilist:
		r.extend((str(len(k)), ':', k))
		encode_func[type(v)](v, r)
	r.append('e')

def encode_byte(x, r):
	r.extend((str(len(x)), ':', str(x)))

encode_func = {}
encode_func[IntType] = encode_int
encode_func[LongType] = encode_int
encode_func[BooleanType] = encode_bool
encode_func[StringType] = encode_string
encode_func[UnicodeType] = encode_unicode
encode_func[ListType] = encode_list
encode_func[TupleType] = encode_list
encode_func[DictType] = encode_dict

encode_func[bytearray] = encode_byte
encode_func[Metainfo] = encode_dict

def bencode(x):
	r = []
	encode_func[type(x)](x, r)
	return ''.join(r)
