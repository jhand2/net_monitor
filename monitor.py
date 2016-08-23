#!/bin/python3
import socket
import struct


def listen():
    '''
    Listens for packets and prints them
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)

    # sock.bind(('localhost', 8080))

    while True:
        # Parse IP info. We'll throw away the sender IP since we'll parse
        # it from the IP header anyway
        packet, _ = sock.recvfrom(65565)

        unpacked_ip = ip_unpack(packet)

        print_packet(unpacked_ip)
        print()


def print_packet(packet):
    for key in packet:
        if (type(packet[key]) is dict):
            print(str(key))
            print_packet(packet[key])
        else:
            print(str(key) + ': ' + str(packet[key]))


def ip_unpack(packet):
    '''
    Unpacks an ip packet
    '''
    ip_header = packet[0:20]  # assuming header length is 20 bytes

    # Format info: first character denotes byte order. > is big endian
    # (network order). All foolowing letters are c types. numbers are
    # like sizeof(char) * 4 in C. They denote array size.
    iph_format = '>BBHHHBBH4s4s'
    iph = struct.unpack(iph_format, ip_header)  # IP header

    # Version and ip header length
    version_iphl = iph[0]
    version = version_iphl >> 4
    iphl = (version_iphl & 0xF) * 4  # times 4 converts to bytes

    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])

    tcp_packet = tcp_unpack(packet[iphl:])

    return {
        'ip_version': version,
        'header_len': iphl,
        'time_to_live': ttl,
        'protocol': protocol,
        'source_address': s_addr,
        'dest_address': d_addr,
        'payload': tcp_packet
    }


def tcp_unpack(packet):
    '''
    Unpacks a tcp packet. Assumes the IP header has already been stripped
    '''
    tcph = struct.unpack('>HHLLBBHHH', packet[:20])

    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_len = (doff_reserved >> 4) * 4

    data = packet[tcph_len:]
    try:
        data = data.decode('utf-8')
    except Exception:
        pass

    return {
        'source_port': source_port,
        'dest_port': dest_port,
        'sequence': sequence,
        'acknowledgement': acknowledgement,
        'header_len': tcph_len,
        'data': data
    }


if __name__ == '__main__':
    listen()
