#!/bin/python3
import socket
import struct

# Create TCP socket


def listen():
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    while True:
        # Parse IP info. We'll throw away the sender IP since we'll parse
        # it from the IP header anyway
        packet, _ = sock.recvfrom(6555)
        ip_header = packet[0:20]

        # Format info: first character denotes byte order. > is big endian
        # (network order). All foolowing letters are c types. numbers are
        # like sizeof(char) * 4 in C.
        iph_format = '>BBHHHBBH4s4s'
        iph = struct.unpack(iph_format, ip_header)

        version_iphl = iph[0]
        version = version_iphl >> 4
        iphl = version_iphl & 0xF

        # iph_len = ihl * 4

        ttl = iph[5]
        protocol = iph[6]
        s_addr = socket.inet_ntoa(iph[8])
        d_addr = socket.inet_ntoa(iph[9])

        unpacked_ip = {
            'ip_version': version,
            'header_len': iphl

        }

        print('IP Header:')
        print('Version: ' + str(version) + '; IP Header Length: ' +
              str(iphl) + '; TTL: ' + str(ttl) + '; Protocol: ' +
              str(protocol) + ' Source Address: ' + str(s_addr) +
              ' Destination Address: ' + str(d_addr), end="\n\n")

        print(str(unpacked_ip))


if __name__ == '__main__':
    listen()
