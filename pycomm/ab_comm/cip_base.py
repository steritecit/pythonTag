# -*- coding: utf-8 -*-
#
# cip_base.py - A set of classes methods and structures  used to implement Ethernet/IP
#
#
# Copyright (c) 2014 Agostino Ruscito <ruscito@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
from binascii import hexlify
import struct
import socket
import random
from pprint import pprint
from os import getpid, urandom
import time

LOGGING_ON = False

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logger = logging.getLogger(__name__)
logger.addHandler(NullHandler())

# -*- coding: utf-8 -*-
#
# cip_const.py - A set of structures and constants used to implement the Ethernet/IP protocol
#
#
# Copyright (c) 2014 Agostino Ruscito <ruscito@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

ELEMENT_ID = {
    "8-bit":  b'\x28',
    "16-bit": b'\x29',
    "32-bit": b'\x2a'
}

CLASS_ID = {
    "8-bit":  b'\x20',
    "16-bit": b'\x21',
}

INSTANCE_ID = {
    "8-bit":  b'\x24',
    "16-bit": b'\x25'
}

ATTRIBUTE_ID = {
    "8-bit": '\x30',
    "16-bit": '\x31'
}

# Path are combined as:
# CLASS_ID + PATHS
# For example PCCC path is CLASS_ID["8-bit"]+PATH["PCCC"] -> 0x20, 0x67, 0x24, 0x01.
PATH = {
    'Connection Manager': b'\x06\x24\x01',
    'Router': b'\x02\x24\x01',
    'Backplane Data Type': b'\x66\x24\x01',
    'PCCC': b'\x67\x24\x01',
    'DHCP Channel A': b'\xa6\x24\x01\x01\x2c\x01',
    'DHCP Channel B': b'\xa6\x24\x01\x02\x2c\x01'
}

ENCAPSULATION_COMMAND = {  # Volume 2: 2-3.2 Command Field UINT 2 byte
    "nop":                b'\x00\x00',
    "list_targets":       b'\x01\x00',
    "list_services":      b'\x04\x00',
    "list_identity":      b'\x63\x00',
    "list_interfaces":    b'\x64\x00',
    "register_session":   b'\x65\x00',
    "unregister_session": b'\x66\x00',
    "send_rr_data":       b'\x6F\x00',
    "send_unit_data":     b'\x70\x00'
}

"""
When a tag is created, an instance of the Symbol Object (Class ID 0x6B) is created
inside the controller.

When a UDT is created, an instance of the Template object (Class ID 0x6C) is
created to hold information about the structure makeup.
"""
CLASS_CODE = {
    "Message Router":     b'\x02',  # Volume 1: 5-1
    "Symbol Object":      b'\x6b',
    "Template Object":    b'\x6c',
    "Connection Manager": b'\x06'  # Volume 1: 3-5
}

CONNECTION_MANAGER_INSTANCE = {
    'Open Request':            b'\x01',
    'Open Format Rejected':    b'\x02',
    'Open Resource  Rejected': b'\x03',
    'Open Other Rejected':     b'\x04',
    'Close Request':           b'\x05',
    'Close Format Request':    b'\x06',
    'Close Other Request':     b'\x07',
    'Connection Timeout':      b'\x08'
}

TAG_SERVICES_REQUEST = {
    "Read Tag":                     0x4c,
    "Read Tag Fragmented":          0x52,
    "Write Tag":                    0x4d,
    "Write Tag Fragmented":         0x53,
    "Read Modify Write Tag":        0x4e,
    "Multiple Service Packet":      0x0a,
    "Get Instance Attributes List": 0x55,
    "Get Attributes":               0x03,
    "Read Template":                0x4c,
}

TAG_SERVICES_REPLY = {
    0xcc: "Read Tag",
    0xd2: "Read Tag Fragmented",
    0xcd: "Write Tag",
    0xd3: "Write Tag Fragmented",
    0xce: "Read Modify Write Tag",
    0x8a: "Multiple Service Packet",
    0xd5: "Get Instance Attributes List",
    0x83: "Get Attributes",
    0xcc: "Read Template"
}


I_TAG_SERVICES_REPLY = {
    "Read Tag": 0xcc,
    "Read Tag Fragmented": 0xd2,
    "Write Tag": 0xcd,
    "Write Tag Fragmented": 0xd3,
    "Read Modify Write Tag": 0xce,
    "Multiple Service Packet": 0x8a,
    "Get Instance Attributes List": 0xd5,
    "Get Attributes": 0x83,
    "Read Template": 0xcc
}


"""
EtherNet/IP Encapsulation Error Codes

Standard CIP Encapsulation Error returned in the cip message header
"""
STATUS = {
    0x0000: "Success",
    0x0001: "The sender issued an invalid or unsupported encapsulation command",
    0x0002: "Insufficient memory",
    0x0003: "Poorly formed or incorrect data in the data portion",
    0x0064: "An originator used an invalid session handle when sending an encapsulation message to the target",
    0x0065: "The target received a message of invalid length",
    0x0069: "Unsupported Protocol Version"
}

"""
MSG Error Codes:

The following error codes have been taken from:

Rockwell Automation Publication
1756-RM003P-EN-P - December 2014
"""
SERVICE_STATUS = {
    0x01: "Connection failure (see extended status)",
    0x02: "Insufficient resource",
    0x03: "Invalid value",
    0x04: "IOI syntax error. A syntax error was detected decoding the Request Path (see extended status)",
    0x05: "Destination unknown, class unsupported, instance \nundefined or structure element undefined (see extended status)",
    0x06: "Insufficient Packet Space",
    0x07: "Connection lost",
    0x08: "Service not supported",
    0x09: "Error in data segment or invalid attribute value",
    0x0A: "Attribute list error",
    0x0B: "State already exist",
    0x0C: "Object state conflict",
    0x0D: "Object already exist",
    0x0E: "Attribute not settable",
    0x0F: "Permission denied",
    0x10: "Device state conflict",
    0x11: "Reply data too large",
    0x12: "Fragmentation of a primitive value",
    0x13: "Insufficient command data",
    0x14: "Attribute not supported",
    0x15: "Too much data",
    0x1A: "Bridge request too large",
    0x1B: "Bridge response too large",
    0x1C: "Attribute list shortage",
    0x1D: "Invalid attribute list",
    0x1E: "Request service error",
    0x1F: "Connection related failure (see extended status)",
    0x22: "Invalid reply received",
    0x25: "Key segment error",
    0x26: "Invalid IOI error",
    0x27: "Unexpected attribute in list",
    0x28: "DeviceNet error - invalid member ID",
    0x29: "DeviceNet error - member not settable",
    0xD1: "Module not in run state",
    0xFB: "Message port not supported",
    0xFC: "Message unsupported data type",
    0xFD: "Message uninitialized",
    0xFE: "Message timeout",
    0xff: "General Error (see extended status)"
}

EXTEND_CODES = {
    0x01: {
        0x0100: "Connection in use",
        0x0103: "Transport not supported",
        0x0106: "Ownership conflict",
        0x0107: "Connection not found",
        0x0108: "Invalid connection type",
        0x0109: "Invalid connection size",
        0x0110: "Module not configured",
        0x0111: "EPR not supported",
        0x0114: "Wrong module",
        0x0115: "Wrong device type",
        0x0116: "Wrong revision",
        0x0118: "Invalid configuration format",
        0x011A: "Application out of connections",
        0x0203: "Connection timeout",
        0x0204: "Unconnected message timeout",
        0x0205: "Unconnected send parameter error",
        0x0206: "Message too large",
        0x0301: "No buffer memory",
        0x0302: "Bandwidth not available",
        0x0303: "No screeners available",
        0x0305: "Signature match",
        0x0311: "Port not available",
        0x0312: "Link address not available",
        0x0315: "Invalid segment type",
        0x0317: "Connection not scheduled"
    },
    0x04: {
        0x0000: "Extended status out of memory",
        0x0001: "Extended status out of instances"
    },
    0x05: {
        0x0000: "Extended status out of memory",
        0x0001: "Extended status out of instances"
    },
    0x1F: {
        0x0203: "Connection timeout"
    },
    0xff: {
        0x7: "Wrong data type",
        0x2001: "Excessive IOI",
        0x2002: "Bad parameter value",
        0x2018: "Semaphore reject",
        0x201B: "Size too small",
        0x201C: "Invalid size",
        0x2100: "Privilege failure",
        0x2101: "Invalid keyswitch position",
        0x2102: "Password invalid",
        0x2103: "No password issued",
        0x2104: "Address out of range",
        0x2105: "Access beyond end of the object",
        0x2106: "Data in use",
        0x2107: "Tag type used n request dose not match the target tag's data type",
        0x2108: "Controller in upload or download mode",
        0x2109: "Attempt to change number of array dimensions",
        0x210A: "Invalid symbol name",
        0x210B: "Symbol does not exist",
        0x210E: "Search failed",
        0x210F: "Task cannot start",
        0x2110: "Unable to write",
        0x2111: "Unable to read",
        0x2112: "Shared routine not editable",
        0x2113: "Controller in faulted mode",
        0x2114: "Run mode inhibited"

    }
}
DATA_ITEM = {
    'Connected':   b'\xb1\x00',
    'Unconnected': b'\xb2\x00'
}

ADDRESS_ITEM = {
    'Connection Based': b'\xa1\x00',
    'Null':             b'\x00\x00',
    'UCMM':             b'\x00\x00'
}

UCMM = {
    'Interface Handle': 0,
    'Item Count': 2,
    'Address Type ID': 0,
    'Address Length': 0,
    'Data Type ID': 0x00b2
}

CONNECTION_SIZE = {
    'Backplane':      b'\x03',     # CLX
    'Direct Network': b'\x02'
}

HEADER_SIZE = 24
EXTENDED_SYMBOL = b'\x91'
BOOL_ONE = 0xff
REQUEST_SERVICE = 0
REQUEST_PATH_SIZE = 1
REQUEST_PATH = 2
SUCCESS = 0
INSUFFICIENT_PACKETS = 6
OFFSET_MESSAGE_REQUEST = 40


FORWARD_CLOSE          = b'\x4e'
UNCONNECTED_SEND       = b'\x52'
FORWARD_OPEN           = b'\x54'
LARGE_FORWARD_OPEN     = b'\x5b'
GET_CONNECTION_DATA    = b'\x56'
SEARCH_CONNECTION_DATA = b'\x57'
GET_CONNECTION_OWNER   = b'\x5a'
MR_SERVICE_SIZE        = 2

PADDING_BYTE =       b'\x00'
PRIORITY =           b'\x0a'
TIMEOUT_TICKS =      b'\x05'
TIMEOUT_MULTIPLIER = b'\x01'
TRANSPORT_CLASS =    b'\xa3'

CONNECTION_PARAMETER = {
    'PLC5': 0x4302,
    'SLC500': 0x4302,
    'CNET': 0x4320,
    'DHP': 0x4302,
    'Default': 0x43f8,
}

"""
Atomic Data Type:

          Bit = Bool
     Bit array = DWORD (32-bit boolean aray)
 8-bit integer = SINT
16-bit integer = UINT
32-bit integer = DINT
  32-bit float = REAL
64-bit integer = LINT

From Rockwell Automation Publication 1756-PM020C-EN-P November 2012:
When reading a BOOL tag, the values returned for 0 and 1 are 0 and 0xff, respectively.
"""

S_DATA_TYPE = {
    'BOOL': 0xc1,
    'SINT': 0xc2,    # Signed 8-bit integer
    'INT': 0xc3,     # Signed 16-bit integer
    'DINT': 0xc4,    # Signed 32-bit integer
    'LINT': 0xc5,    # Signed 64-bit integer
    'USINT': 0xc6,   # Unsigned 8-bit integer
    'UINT': 0xc7,    # Unsigned 16-bit integer
    'UDINT': 0xc8,   # Unsigned 32-bit integer
    'ULINT': 0xc9,   # Unsigned 64-bit integer
    'REAL': 0xca,    # 32-bit floating point
    'LREAL': 0xcb,   # 64-bit floating point
    'STIME': 0xcc,   # Synchronous time
    'DATE': 0xcd,
    'TIME_OF_DAY': 0xce,
    'DATE_AND_TIME': 0xcf,
    'STRING': 0xd0,   # character string (1 byte per character)
    'BYTE': 0xd1,     # byte string 8-bits
    'WORD': 0xd2,     # byte string 16-bits
    'DWORD': 0xd3,    # byte string 32-bits
    'LWORD': 0xd4,    # byte string 64-bits
    'STRING2': 0xd5,  # character string (2 byte per character)
    'FTIME': 0xd6,    # Duration high resolution
    'LTIME': 0xd7,    # Duration long
    'ITIME': 0xd8,    # Duration short
    'STRINGN': 0xd9,  # character string (n byte per character)
    'SHORT_STRING': 0xda,  # character string (1 byte per character, 1 byte length indicator)
    'TIME': 0xdb,     # Duration in milliseconds
    'EPATH': 0xdc,    # CIP Path segment
    'ENGUNIT': 0xdd,  # Engineering Units
    'STRINGI': 0xde   # International character string
}

I_DATA_TYPE = {
    0xc1: 'BOOL',
    0xc2: 'SINT',    # Signed 8-bit integer
    0xc3: 'INT',     # Signed 16-bit integer
    0xc4: 'DINT',    # Signed 32-bit integer
    0xc5: 'LINT',    # Signed 64-bit integer
    0xc6: 'USINT',   # Unsigned 8-bit integer
    0xc7: 'UINT',    # Unsigned 16-bit integer
    0xc8: 'UDINT',   # Unsigned 32-bit integer
    0xc9: 'ULINT',   # Unsigned 64-bit integer
    0xca: 'REAL',    # 32-bit floating point
    0xcb: 'LREAL',   # 64-bit floating point
    0xcc: 'STIME',   # Synchronous time
    0xcd: 'DATE',
    0xce: 'TIME_OF_DAY',
    0xcf: 'DATE_AND_TIME',
    0xd0: 'STRING',   # character string (1 byte per character)
    0xd1: 'BYTE',     # byte string 8-bits
    0xd2: 'WORD',     # byte string 16-bits
    0xd3: 'DWORD',    # byte string 32-bits
    0xd4: 'LWORD',    # byte string 64-bits
    0xd5: 'STRING2',  # character string (2 byte per character)
    0xd6: 'FTIME',    # Duration high resolution
    0xd7: 'LTIME',    # Duration long
    0xd8: 'ITIME',    # Duration short
    0xd9: 'STRINGN',  # character string (n byte per character)
    0xda: 'SHORT_STRING',  # character string (1 byte per character, 1 byte length indicator)
    0xdb: 'TIME',     # Duration in milliseconds
    0xdc: 'EPATH',    # CIP Path segment
    0xdd: 'ENGUNIT',  # Engineering Units
    0xde: 'STRINGI'    # International character string
}

REPLAY_INFO = {
    0x4e: 'FORWARD_CLOSE (4E,00)',
    0x52: 'UNCONNECTED_SEND (52,00)',
    0x54: 'FORWARD_OPEN (54,00)',
    0x6f: 'send_rr_data (6F,00)',
    0x70: 'send_unit_data (70,00)',
    0x00: 'nop',
    0x01: 'list_targets',
    0x04: 'list_services',
    0x63: 'list_identity',
    0x64: 'list_interfaces',
    0x65: 'register_session',
    0x66: 'unregister_session',
}

PCCC_DATA_TYPE = {
    'N': b'\x89',
    'B': b'\x85',
    'T': b'\x86',
    'C': b'\x87',
    'S': b'\x84',
    'F': b'\x8a',
    'ST': b'\x8d',
    'A': b'\x8e',
    'R': b'\x88',
    'O': b'\x8b',
    'I': b'\x8c'
}

PCCC_DATA_SIZE = {
    'N': 2,
    # 'L': 4,
    'B': 2,
    'T': 6,
    'C': 6,
    'S': 2,
    'F': 4,
    'ST': 84,
    'A': 2,
    'R': 6,
    'O': 2,
    'I': 2
}

PCCC_CT = {
    'PRE': 1,
    'ACC': 2,
    'EN': 15,
    'TT': 14,
    'DN': 13,
    'CU': 15,
    'CD': 14,
    'OV': 12,
    'UN': 11,
    'UA': 10
}

PCCC_ERROR_CODE = {
    -2: "Not Acknowledged (NAK)",
    -3: "No Reponse, Check COM Settings",
    -4: "Unknown Message from DataLink Layer",
    -5: "Invalid Address",
    -6: "Could Not Open Com Port",
    -7: "No data specified to data link layer",
    -8: "No data returned from PLC",
    -20: "No Data Returned",
    16: "Illegal Command or Format, Address may not exist or not enough elements in data file",
    32: "PLC Has a Problem and Will Not Communicate",
    48: "Remote Node Host is Missing, Disconnected, or Shut Down",
    64: "Host Could Not Complete Function Due To Hardware Fault",
    80: "Addressing problem or Memory Protect Rungs",
    96: "Function not allows due to command protection selection",
    112: "Processor is in Program mode",
    128: "Compatibility mode file missing or communication zone problem",
    144: "Remote node cannot buffer command",
    240: "Error code in EXT STS Byte"
}

class PycommError(Exception):
    pass

class CommError(PycommError):
    pass


class DataError(PycommError):
    pass

def build_padding(valueSize):
    return ' '*(50-valueSize)

def format_print_log(funcname, methodname, title, value):
    print(build_padding(len(title)), title, value)

def log(func):
    def wrapper(*args, **kwargs):
        if LOGGING_ON:
            print('\nFUNCTION: ', func.__name__)
            print('---------------')
            for arg in args:
                print(' -- Argument:', arg, ' TYPE:', type(arg))
            for key, val in kwargs.items():
                print(' -- KW Argument:', key, val, ' TYPE:', type(val))
            value = func(*args, **kwargs)
            print('   ------  Return Value: ', value, ' TYPE:', type(value))
            time.sleep(2)

        return func(*args, **kwargs)
    return wrapper

def el_logger(funcname, methodname, value):
    print('*'*50, '[ ','Function:', funcname, '()', ' ]', '*'*50)
    print('Var || Method:', methodname)
    format_print_log(funcname, methodname, 'Representation:', repr(value))
    try:
        hex_data = hexlify(value)
        text_string = hex_data.decode('utf-8')
        format_print_log(funcname, methodname, 'Hex Data:', hex_data) # Two bytes values 0 and 255
        format_print_log(funcname, methodname, 'String:', text_string)
        
        
    except:
        msg = 'Source: el_logger(): Error: Datatype mismatch for hexConversion. Type Passed: %s' % type(value)
        format_print_log(funcname, methodname, 'Raw', msg)
    print("")
    print("")

@log
def pack_sint(n):
    return struct.pack('b', n)


@log
def pack_usint(n):
    return struct.pack('B', n)


@log
def pack_int(n):
    """pack 16 bit into 2 bytes little endian"""
    return struct.pack('<h', n)


@log
def pack_uint(n):
    """pack 16 bit into 2 bytes little endian"""
    return struct.pack('<H', n)


@log
def pack_dint(n):
    """pack 32 bit into 4 bytes little endian"""
    return struct.pack('<i', n)


@log
def pack_real(r):
    """unpack 4 bytes little endian to int"""
    return struct.pack('<f', r)


@log
def pack_lint(l):
    """unpack 4 bytes little endian to int"""
    return struct.pack('<q', l)


@log
def unpack_bool(st):
    if not (int(struct.unpack('B', st[0])[0]) == 0):
        return 1
    return 0


@log
def unpack_sint(st):
    return int(struct.unpack('b', st[0])[0])


@log
def unpack_usint(st):
    return int(struct.unpack('B', bytes([st[0]]))[0])


@log
def unpack_int(st):
    """unpack 2 bytes little endian to int"""
    return int(struct.unpack('<h', st[0:2])[0])

@log
def unpack_uint(st):
    """unpack 2 bytes little endian to int"""
    return int(struct.unpack('<H', st[0:2])[0])


@log
def unpack_dint(st):
    """unpack 4 bytes little endian to int"""
    return int(struct.unpack('<i', st[0:4])[0])


@log
def unpack_real(st):
    """unpack 4 bytes little endian to int"""
    return float(struct.unpack('<f', st[0:4])[0])


@log
def unpack_lint(st):
    """unpack 4 bytes little endian to int"""
    return int(struct.unpack('<q', st[0:8])[0])


@log
def get_bit(value, idx):
    """:returns value of bit at position idx"""
    return (value & (1 << idx)) != 0


PACK_DATA_FUNCTION = {
    'BOOL': pack_sint,
    'SINT': pack_sint,    # Signed 8-bit integer
    'INT': pack_int,     # Signed 16-bit integer
    'UINT': pack_uint,    # Unsigned 16-bit integer
    'USINT': pack_usint,  # Unsigned Byte Integer
    'DINT': pack_dint,    # Signed 32-bit integer
    'REAL': pack_real,    # 32-bit floating point
    'LINT': pack_lint,
    'BYTE': pack_sint,     # byte string 8-bits
    'WORD': pack_uint,     # byte string 16-bits
    'DWORD': pack_dint,    # byte string 32-bits
    'LWORD': pack_lint    # byte string 64-bits
}


UNPACK_DATA_FUNCTION = {
    'BOOL': unpack_bool,
    'SINT': unpack_sint,    # Signed 8-bit integer
    'INT': unpack_int,     # Signed 16-bit integer
    'UINT': unpack_uint,    # Unsigned 16-bit integer
    'USINT': unpack_usint,  # Unsigned Byte Integer
    'DINT': unpack_dint,    # Signed 32-bit integer
    'REAL': unpack_real,    # 32-bit floating point,
    'LINT': unpack_lint,
    'BYTE': unpack_sint,     # byte string 8-bits
    'WORD': unpack_uint,     # byte string 16-bits
    'DWORD': unpack_dint,    # byte string 32-bits
    'LWORD': unpack_lint    # byte string 64-bits
}


DATA_FUNCTION_SIZE = {
    'BOOL': 1,
    'SINT': 1,    # Signed 8-bit integer
    'USINT': 1,  # Unisgned 8-bit integer
    'INT': 2,     # Signed 16-bit integer
    'UINT': 2,    # Unsigned 16-bit integer
    'DINT': 4,    # Signed 32-bit integer
    'REAL': 4,    # 32-bit floating point
    'LINT': 8,
    'BYTE': 1,     # byte string 8-bits
    'WORD': 2,     # byte string 16-bits
    'DWORD': 4,    # byte string 32-bits
    'LWORD': 8    # byte string 64-bits
}

UNPACK_PCCC_DATA_FUNCTION = {
    'N': unpack_int,
    'B': unpack_int,
    'T': unpack_int,
    'C': unpack_int,
    'S': unpack_int,
    'F': unpack_real,
    'A': unpack_sint,
    'R': unpack_dint,
    'O': unpack_int,
    'I': unpack_int
}

PACK_PCCC_DATA_FUNCTION = {
    'N': pack_int,
    'B': pack_int,
    'T': pack_int,
    'C': pack_int,
    'S': pack_int,
    'F': pack_real,
    'A': pack_sint,
    'R': pack_dint,
    'O': pack_int,
    'I': pack_int
}


@log
def print_bytes_line(msg):
    out = ''
    for ch in msg:
        out += "{:0>2x}".format(ch)
    return out


@log
def print_bytes_msg(msg, info=''):
    out = info
    new_line = True
    line = 0
    column = 0
    for idx, ch in enumerate(msg):
        if new_line:
            out += "\n({:0>4d}) ".format(line * 10)
            new_line = False
        out += "{:0>2x} ".format(ch)
        if column == 9:
            new_line = True
            column = 0
            line += 1
        else:
            column += 1
    return out


@log
def get_extended_status(msg, start):
    status = unpack_usint(msg[start:start+1])
    # send_rr_data
    # 42 General Status
    # 43 Size of additional status
    # 44..n additional status

    # send_unit_data
    # 48 General Status
    # 49 Size of additional status
    # 50..n additional status
    extended_status_size = (unpack_usint(msg[start+1:start+2]))*2
    extended_status = 0
    if extended_status_size != 0:
        # There is an additional status
        if extended_status_size == 1:
            extended_status = unpack_usint(msg[start+2:start+3])
        elif extended_status_size == 2:
            extended_status = unpack_uint(msg[start+2:start+4])
        elif extended_status_size == 4:
            extended_status = unpack_dint(msg[start+2:start+6])
        else:
            return 'Extended Status Size Unknown'
    try:
        return '{0}'.format(EXTEND_CODES[status][extended_status])
    except LookupError:
        return "Extended Status info not present"


@log
def create_tag_rp(tag, multi_requests=False):
    """ Create tag Request Packet

    It returns the request packed wrapped around the tag passed.
    If any error it returns none
    """


    el_logger('create_tag_rp', 'tag:', tag)
    tags = tag.encode().split(b'.')
    el_logger('create_tag_rp', 'tags:', tags)
    rp = []
    index = []
    for tag in tags:
        el_logger('create_tag_rp', 'tag.forLoop.tag:', tag)
        add_index = False
        # Check if is an array tag
        #if tag.find(b'[') != -1:
        if b'[' in tag:
            # Remove the last square bracket
            tag = tag[:len(tag)-1]
            # Isolate the value inside bracket
            inside_value = tag[tag.find(b'[')+1:]
            # Now split the inside value in case part of multidimensional array
            index = inside_value.split(b',')
            # Flag the existence of one o more index
            add_index = True
            # Get only the tag part
            tag = tag[:tag.find(b'[')]
        el_logger('create_tag_rp', 'tag.forLoop.manipBytesTag:', tag)
        tag_length = len(tag)
        el_logger('create_tag_rp', 'tag.forLoop.tag_length:', tag_length)
        # Create the request path
        rp.append(EXTENDED_SYMBOL)  # ANSI Ext. symbolic segment
        el_logger('create_tag_rp', 'tag.forLoop.EXTENDED_SYMBOL:', EXTENDED_SYMBOL)
        rp.append(bytes([tag_length]))  # Length of the tag
        el_logger('create_tag_rp', 'tag.forLoop.bytes([tag_length]):', bytes([tag_length]))
        # Add the tag to the Request path
        el_logger('create_tag_rp', 'tag.forLoop.rp-State:', rp)
        for char in tag:
            rp.append(bytes([char]))
            el_logger('create_tag_rp', 'tag.forLoop.char():', bytes([char]))
        el_logger('create_tag_rp', 'tag.forLoop.rp-State after TagName:', rp)
        # Add pad byte because total length of Request path must be word-aligned
        if tag_length % 2:
            rp.append(PADDING_BYTE)
            el_logger('create_tag_rp', 'tag.forLoop.PADDIN_Byte:', PADDING_BYTE)
        el_logger('create_tag_rp', 'tag.forLoop.rp-State after padding:', rp)
        # Add any index
        if add_index:
            for idx in index:
                val = int(idx)
                if val <= 0xff:
                    rp.append(ELEMENT_ID["8-bit"])
                    rp.append(pack_usint(val))
                elif val <= 0xffff:
                    rp.append(ELEMENT_ID["16-bit"]+PADDING_BYTE)
                    rp.append(pack_uint(val))
                elif val <= 0xfffffffff:
                    rp.append(ELEMENT_ID["32-bit"]+PADDING_BYTE)
                    rp.append(pack_dint(val))
                else:
                    # Cannot create a valid request packet
                    return None

    # At this point the Request Path is completed,
    if multi_requests:
        request_path = bytes([len(rp)//2]) + b''.join(rp)
        el_logger('create_tag_rp', 'tag.forLoop.PADDIN_Byte:', PADDING_BYTE)
    else:
        request_path = b''.join(rp)
        el_logger('create_tag_rp', 'tag.forLoop.request_path:', request_path)
    return request_path


@log
def build_common_packet_format(message_type, message, addr_type, addr_data=None, timeout=10):
    """ build_common_packet_format

    It creates the common part for a CIP message. Check Volume 2 (page 2.22) of CIP specification  for reference
    """

    msg = pack_dint(0)   # Interface Handle: shall be 0 for CIP
    el_logger('build_common_packet_format','msg',msg)
    msg += pack_uint(timeout)   # timeout
    el_logger('build_common_packet_format','pack_uint(timeout)',pack_uint(timeout) )
    msg += pack_uint(2)  # Item count: should be at list 2 (Address and Data)
    el_logger('build_common_packet_format','pack_uint(2)',pack_uint(2))
    msg += addr_type  # Address Item Type ID
    el_logger('build_common_packet_format','addr_type',addr_type)

    if addr_data is not None:
        msg += pack_uint(len(addr_data))  # Address Item Length
        el_logger('build_common_packet_format','pack_uint(len(addr_data))',pack_uint(len(addr_data)))
        msg += addr_data
        el_logger('build_common_packet_format','addr_data',addr_data)
    else:
        msg += pack_uint(0)  # Address Item Length
        el_logger('build_common_packet_format','pack_uint(0)',pack_uint(0))
    msg += message_type  # Data Type ID
    el_logger('build_common_packet_format','message_type',message_type)
    msg += pack_uint(len(message))   # Data Item Length
    el_logger('build_common_packet_format','pack_uint(len(message))',pack_uint(len(message)))
    msg += message
    el_logger('build_common_packet_format','message',message)
    return msg


@log
def build_multiple_service(rp_list, sequence=None):

    mr = []
    if sequence is not None:
        mr.append(pack_uint(sequence))
    print('SEQUENCE', sequence)
    mr.append(bytes([TAG_SERVICES_REQUEST["Multiple Service Packet"]]))  # the Request Service
    mr.append(pack_usint(2))                 # the Request Path Size length in word
    mr.append(CLASS_ID["8-bit"])
    mr.append(CLASS_CODE["Message Router"])
    mr.append(INSTANCE_ID["8-bit"])
    mr.append(pack_usint(1))                 # Instance 1
    mr.append(pack_uint(len(rp_list)))      # Number of service contained in the request

    # Offset calculation
    offset = (len(rp_list) * 2) + 2
    for index, rp in enumerate(rp_list):
        if index == 0:
            mr.append(pack_uint(offset))   # Starting offset
        else:
            mr.append(pack_uint(offset))
        offset += len(rp)

    for rp in rp_list:
        mr.append(rp)
    return mr


@log
def parse_multiple_request(message, tags, typ):
    """ parse_multi_request
    This function should be used to parse the message replayed to a multi request service rapped around the
    send_unit_data message.


    :param message: the full message returned from the PLC
    :param tags: The list of tags to be read
    :param typ: to specify if multi request service READ or WRITE
    :return: a list of tuple in the format [ (tag name, value, data type), ( tag name, value, data type) ].
             In case of error the tuple will be (tag name, None, None)
    """
    offset = 50
    position = 50
    number_of_service_replies = unpack_uint(message[offset:offset+2])
    tag_list = []
    for index in range(number_of_service_replies):
        position += 2
        start = offset + unpack_uint(message[position:position+2])
        general_status = unpack_usint(message[start+2:start+3])

        if general_status == 0:
            if typ == "READ":
                data_type = unpack_uint(message[start+4:start+6])
                try:
                    value_begin = start + 6
                    value_end = value_begin + DATA_FUNCTION_SIZE[I_DATA_TYPE[data_type]]
                    value = message[value_begin:value_end]
                    tag_list.append((tags[index],
                                    UNPACK_DATA_FUNCTION[I_DATA_TYPE[data_type]](value),
                                    I_DATA_TYPE[data_type]))
                except LookupError:
                    tag_list.append((tags[index], None, None))
            else:
                tag_list.append((tags[index] + ('GOOD',)))
        else:
            if typ == "READ":
                tag_list.append((tags[index], None, None))
            else:
                tag_list.append((tags[index] + ('BAD',)))
    return tag_list


class Socket:

    def __init__(self, timeout=5.0):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(timeout)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def connect(self, host, port):
        try:
            self.sock.connect((host, port))
        except socket.timeout:
            raise CommError("Socket timeout during connection.")

    def send(self, msg, timeout=0):
        if timeout != 0:
            self.sock.settimeout(timeout)
        total_sent = 0
        while total_sent < len(msg):
            try:
                sent = self.sock.send(msg[total_sent:])
                if sent == 0:
                    raise CommError("socket connection broken.")
                total_sent += sent
            except socket.error:
                raise CommError("socket connection broken.")
        return total_sent

    def receive(self, timeout=0):
        if timeout != 0:
            self.sock.settimeout(timeout)
        msg_len = 28
        chunks = []
        bytes_recd = 0
        one_shot = True
        while bytes_recd < msg_len:
            try:
                chunk = self.sock.recv(min(msg_len - bytes_recd, 2048))
                if chunk == '':
                    raise CommError("socket connection broken.")
                if one_shot:
                    data_size = int(struct.unpack('<H', chunk[2:4])[0])  # Length
                    msg_len = HEADER_SIZE + data_size
                    one_shot = False

                chunks.append(chunk)
                bytes_recd += len(chunk)
            except socket.error as e:
                raise CommError(e)
        return b''.join(chunks)

    def close(self):
        self.sock.close()


def parse_symbol_type(symbol):
    """ parse_symbol_type

    It parse the symbol to Rockwell Spec
    :param symbol: the symbol associated to a tag
    :return: A tuple containing information about the tag
    """
    pass

    return None


class Base(object):
    _sequence = 0


    def __init__(self):
        if Base._sequence == 0:
            Base._sequence = getpid()
        else:
            Base._sequence = Base._get_sequence()

        self.__version__ = '0.3'
        self.__sock = None
        self.__direct_connections = False
        self._session = 0
        self._connection_opened = False
        self._reply = None
        self._message = None
        self._target_cid = None
        self._target_is_connected = False
        self._tag_list = []
        self._buffer = {}
        self._device_description = "Device Unknown"
        self._last_instance = 0
        self._byte_offset = 0
        self._last_position = 0
        self._more_packets_available = False
        self._last_tag_read = ()
        self._last_tag_write = ()
        self._status = (0, "")
        self._output_raw = False    # indicating value should be output as raw (hex)

        self.attribs = {
                'context':          '_pycomm_',
                'protocol version': 1,
                'rpi':              5000,
                'port':             0xAF12,
                'timeout':          10,
                'backplane':        1,
                'cpu slot':         0,
                'option':           0,
                'cid':              b'\x27\x04\x19\x71',
                'csn':              b'\x27\x04',
                'vid':              b'\x09\x10',
                'vsn':              b'\x09\x10\x19\x71',
                'name':             'Base',
                'ip address':       None}

    def __len__(self):
        return len(self.attribs)

    def __getitem__(self, key):
        return self.attribs[key]

    def __setitem__(self, key, value):
        self.attribs[key] = value

    def __delitem__(self, key):
        try:
            del self.attribs[key]
        except LookupError:
            pass

    def __iter__(self):
        return iter(self.attribs)

    def __contains__(self, item):
        return item in self.attribs

    def _check_reply(self):
        raise Socket.ImplementationError("The method has not been implemented")

    @staticmethod
    def _get_sequence():
        """ Increase and return the sequence used with connected messages

        :return: The New sequence
        """
        if Base._sequence < 65535:
            Base._sequence += 1
        else:
            Base._sequence = getpid() % 65535
        el_logger('base. _get_sequence()','Sequence:',Base._sequence)
        return Base._sequence

    def nop(self):
        """ No replay command

        A NOP provides a way for either an originator or target to determine if the TCP connection is still open.
        """
        self._message = self.build_header(ENCAPSULATION_COMMAND['nop'], 0)
        self._send()

    def __repr__(self):
        return self._device_description

    def generate_cid(self):
        #self.attribs['cid'] = '{0}{1}{2}{3}'.format(chr(random.randint(0, 255)), chr(random.randint(0, 255))
        #                                            , chr(random.randint(0, 255)), chr(random.randint(0, 255)))
        self.attribs['cid'] = urandom(4)

    def generate_vsn(self):
        #self.attribs['vsn'] = '{0}{1}{2}{3}'.format(chr(random.randint(0, 255)), chr(random.randint(0, 255))
        #                                            , chr(random.randint(0, 255)), chr(random.randint(0, 255)))
        self.attribs['vsn'] = urandom(4)

    def description(self):
        return self._device_description

    def list_identity(self):
        """ ListIdentity command to locate and identify potential target

        return true if the replay contains the device description
        """
        self._message = self.build_header(ENCAPSULATION_COMMAND['list_identity'], 0)
        self._send()
        self._receive()
        if self._check_reply():
            try:
                self._device_description = self._reply[63:-1]
                return True
            except Exception as e:
                raise CommError(e)
        return False

    def send_rr_data(self, msg):
        """ SendRRData transfer an encapsulated request/reply packet between the originator and target

        :param msg: The message to be send to the target
        :return: the replay received from the target
        """
        self._message = self.build_header(ENCAPSULATION_COMMAND["send_rr_data"], len(msg))
        self._message += msg
        self._send()
        self._receive()
        return self._check_reply()

    def send_unit_data(self, msg):
        """ SendUnitData send encapsulated connected messages.

        :param msg: The message to be send to the target
        :return: the replay received from the target
        """
        self._message = self.build_header(ENCAPSULATION_COMMAND["send_unit_data"], len(msg))
        self._message += msg
        self._send()
        self._receive()
        return self._check_reply()

    def get_status(self):
        """ Get the last status/error

        This method can be used after any call to get any details in case of error
        :return: A tuple containing (error group, error message)
        """
        return self._status

    def clear(self):
        """ Clear the last status/error

        :return: return am empty tuple
        """
        self._status = (0, "")

    def build_header(self, command, length):
        """ Build the encapsulate message header

        The header is 24 bytes fixed length, and includes the command and the length of the optional data portion.

         :return: the headre
        """
        try:
            h = command
            h += pack_uint(length)                      # Length UINT
            h += pack_dint(self._session)                # Session Handle UDINT
            h += pack_dint(0)                           # Status UDINT
            h += self.attribs['context'].encode()                # Sender Context 8 bytes
            h += pack_dint(self.attribs['option'])      # Option UDINT
            return h
        except Exception as e:
            raise CommError(e)

    def register_session(self):
        """ Register a new session with the communication partner

        :return: None if any error, otherwise return the session number
        """
        if self._session:
            return self._session

        self._session = 0
        self._message = self.build_header(ENCAPSULATION_COMMAND['register_session'], 4)
        self._message += pack_uint(self.attribs['protocol version'])
        self._message += pack_uint(0)
        self._send()
        self._receive()
        if self._check_reply():
            self._session = unpack_dint(self._reply[4:8])
            logger.debug("Session ={0} has been registered.".format(print_bytes_line(self._reply[4:8])))
            return self._session

        self._status = 'Warning ! the session has not been registered.'
        logger.warning(self._status)
        return None

    def forward_open(self):
        """ CIP implementation of the forward open message

        Refer to ODVA documentation Volume 1 3-5.5.2

        :return: False if any error in the replayed message
        """

        if self._session == 0:
            self._status = (4, "A session need to be registered before to call forward_open.")
            raise CommError("A session need to be registered before to call forward open")

        forward_open_msg = [
            FORWARD_OPEN,
            pack_usint(2),
            CLASS_ID["8-bit"],
            CLASS_CODE["Connection Manager"],  # Volume 1: 5-1
            INSTANCE_ID["8-bit"],
            CONNECTION_MANAGER_INSTANCE['Open Request'],
            PRIORITY,
            TIMEOUT_TICKS,
            pack_dint(0),
            self.attribs['cid'],
            self.attribs['csn'],
            self.attribs['vid'],
            self.attribs['vsn'],
            TIMEOUT_MULTIPLIER,
            b'\x00\x00\x00',
            pack_dint(self.attribs['rpi'] * 1000),
            pack_uint(CONNECTION_PARAMETER['Default']),
            pack_dint(self.attribs['rpi'] * 1000),
            pack_uint(CONNECTION_PARAMETER['Default']),
            TRANSPORT_CLASS,  # Transport Class
            # CONNECTION_SIZE['Backplane'],
            # pack_usint(self.attribs['backplane']),
            # pack_usint(self.attribs['cpu slot']),
            CLASS_ID["8-bit"],
            CLASS_CODE["Message Router"],
            INSTANCE_ID["8-bit"],
            pack_usint(1)
        ]
        el_logger('forward_open', 'forward_open_msg',
                  forward_open_msg)

        if self.__direct_connections:
            forward_open_msg[20:1] = [
                CONNECTION_SIZE['Direct Network'],
            ]
        else:
            forward_open_msg[20:3] = [
                CONNECTION_SIZE['Backplane'],
                pack_usint(self.attribs['backplane']),
                pack_usint(self.attribs['cpu slot'])
            ]

        if self.send_rr_data(
                build_common_packet_format(DATA_ITEM['Unconnected'], b''.join(forward_open_msg), ADDRESS_ITEM['UCMM'],)):
            self._target_cid = self._reply[44:48]
            self._target_is_connected = True
            return True
        self._status = (4, "forward_open returned False")
        return False

    def forward_close(self):
        """ CIP implementation of the forward close message

        Each connection opened with the froward open message need to be closed.
        Refer to ODVA documentation Volume 1 3-5.5.3

        :return: False if any error in the replayed message
        """

        if self._session == 0:
            self._status = (5, "A session need to be registered before to call forward_close.")
            raise CommError("A session need to be registered before to call forward_close.")

        forward_close_msg = [
            FORWARD_CLOSE,
            pack_usint(2),
            CLASS_ID["8-bit"],
            CLASS_CODE["Connection Manager"],  # Volume 1: 5-1
            INSTANCE_ID["8-bit"],
            CONNECTION_MANAGER_INSTANCE['Open Request'],
            PRIORITY,
            TIMEOUT_TICKS,
            self.attribs['csn'],
            self.attribs['vid'],
            self.attribs['vsn'],
            # CONNECTION_SIZE['Backplane'],
            # '\x00',     # Reserved
            # pack_usint(self.attribs['backplane']),
            # pack_usint(self.attribs['cpu slot']),
            CLASS_ID["8-bit"],
            CLASS_CODE["Message Router"],
            INSTANCE_ID["8-bit"],
            pack_usint(1)
        ]

        if self.__direct_connections:
            forward_close_msg[11:2] = [
                CONNECTION_SIZE['Direct Network'],
                b'\x00'
            ]
        else:
            forward_close_msg[11:4] = [
                CONNECTION_SIZE['Backplane'],
                b'\x00',
                pack_usint(self.attribs['backplane']),
                pack_usint(self.attribs['cpu slot'])
            ]

        if self.send_rr_data(
                build_common_packet_format(DATA_ITEM['Unconnected'], b''.join(forward_close_msg), ADDRESS_ITEM['UCMM'])):
            self._target_is_connected = False
            return True
        self._status = (5, "forward_close returned False")
        logger.warning(self._status)
        return False

    def un_register_session(self):
        """ Un-register a connection

        """
        self._message = self.build_header(ENCAPSULATION_COMMAND['unregister_session'], 0)
        self._send()
        self._session = None

    def _send(self):
        """
        socket send
        :return: true if no error otherwise false
        """
        try:
            logger.debug(print_bytes_msg(self._message, '-------------- SEND --------------'))
            self.__sock.send(self._message)
        except Exception as e:
            # self.clean_up()
            raise CommError(e)

    def _receive(self):
        """
        socket receive
        :return: true if no error otherwise false
        """
        try:
            self._reply = self.__sock.receive()
            logger.debug(print_bytes_msg(self._reply, '----------- RECEIVE -----------'))
        except Exception as e:
            # self.clean_up()
            raise CommError(e)

    def open(self, ip_address, direct_connection=False):
        """
        socket open
        :param: ip address to connect to and type of connection. By default direct connection is disabled
        :return: true if no error otherwise false
        """
        # set type of connection needed
        self.__direct_connections = direct_connection

        # handle the socket layer
        if not self._connection_opened:
            try:
                if self.__sock is None:
                    self.__sock = Socket()
                self.__sock.connect(ip_address, self.attribs['port'])
                self._connection_opened = True
                self.attribs['ip address'] = ip_address
                self.generate_cid()
                self.generate_vsn()
                if self.register_session() is None:
                    self._status = (13, "Session not registered")
                    return False

                # not sure but maybe I can remove this because is used to clean up any previous unclosed connection
                self.forward_close()
                return True
            except Exception as e:
                # self.clean_up()
                raise CommError(e)

    def close(self):
        """
        socket close
        :return: true if no error otherwise false
        """
        error_string = ''
        try:
            if self._target_is_connected:
                self.forward_close()
            if self._session != 0:
                self.un_register_session()
        except Exception as e:
            error_string += "Error on close() -> session Err: %s" % e.message
            logger.warning(error_string)

        # %GLA must do a cleanup __sock.close()
        try:
            if self.__sock:
                self.__sock.close()
        except Exception as e:
            error_string += "; close() -> __sock.close Err: %s" % e.message
            logger.warning(error_string)

        self.clean_up()

        if error_string:
            raise CommError(error_string)

















    def clean_up(self):
        self.__sock = None
        self._target_is_connected = False
        self._session = 0
        self._connection_opened = False

    def is_connected(self):
        return self._connection_opened
