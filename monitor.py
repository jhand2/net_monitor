#!/bin/python3
import socket
import struct
import threading
import datetime
from pymongo import MongoClient

stop_signal = False
packets = []
packets_lock = threading.Lock()

client = MongoClient('localhost', 27017)
db = client.test


def packet_dump(beginning_time):
    '''
    Gets all packets since the last packet dump and collects meta data
    about packets flowing over the network.
    '''
    global packets

    # do locking operations
    packets_lock.acquire(blocking=True)
    tmp = packets
    packets = []
    packets_lock.release()

    seconds = 5
    stats = {
        "tcp_per_second": len(tmp) / seconds,
        "start_time": beginning_time,
        "end_time": datetime.datetime.now()
    }
    col = db.sec_stats
    col.insert_one(stats)


def listen():
    '''
    Listens for packets and prints them
    '''
    global stop_signal
    global packets
    global packets_lock

    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
    print("Listening for traffic")

    while not stop_signal:
        # Parse IP info. We'll throw away the sender IP since we'll parse
        # it from the IP header anyway
        packet, addr = sock.recvfrom(65535)

        unpacked_eth = _eth_unpack(packet)

        if unpacked_eth is not None:
            net_proto = unpacked_eth["protocol"]
            trans_proto = unpacked_eth["ip_packet"]["protocol"]

            # Only look at tcp/ip packets
            if net_proto == 8 and trans_proto == 6:
                packets_lock.acquire(blocking=True)
                packets.append(unpacked_eth)
                packets_lock.release()


def get_mac_addr(a):
    '''
    Converts a mac address from binary to a human readable format
    '''
    b = map('{:02x}'.format, a)
    return ':'.join(b).upper()


def print_packet(packet):
    for key in packet:
        if (type(packet[key]) is dict):
            print(str(key))
            print_packet(packet[key])
        else:
            print(str(key) + ': ' + str(packet[key]))


def _eth_unpack(packet):
    eth_header = packet[:14]
    try:
        eth = struct.unpack('!6s6sH', eth_header)
    except struct.error:
        return None
    eth_proto = socket.ntohs(eth[2])
    dest_mac = get_mac_addr(packet[0:6])
    source_mac = get_mac_addr(packet[6:12])

    return {
        "protocol": eth_proto,
        "dest_mac": dest_mac,
        "source_mac": source_mac,
        "ip_packet": _ip_unpack(packet[14:])
    }


def _ip_unpack(packet):
    '''
    Unpacks an ip packet
    '''
    ip_header = packet[0:20]  # assuming header length is 20 bytes

    # Format info: first character denotes byte order. > is big endian
    # (network order). All foolowing letters are c types. numbers are
    # like sizeof(char) * 4 in C. They denote array size.
    iph_format = '>BBHHHBBH4s4s'
    try:
        iph = struct.unpack(iph_format, ip_header)  # IP header
    except struct.error:
        return None

    # Version and ip header length
    version_iphl = iph[0]
    version = version_iphl >> 4
    iphl = (version_iphl & 0xF) * 4  # times 4 converts to bytes

    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])

    tcp_packet = _tcp_unpack(packet[iphl:])

    return {
        'ip_version': version,
        'header_len': iphl,
        'time_to_live': ttl,
        'protocol': protocol,
        'source_address': s_addr,
        'dest_address': d_addr,
        'payload': tcp_packet
    }


def _tcp_unpack(packet):
    '''
    Unpacks a tcp packet. Assumes the IP header has already been stripped
    '''
    try:
        tcph = struct.unpack('>HHLLBBHHH', packet[:20])
    except struct.error:
        return None

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


def schedule_packet_dump(start_time):
    now = datetime.datetime.now()
    threading.Timer(5.0, schedule_packet_dump, (now,)).start()
    packet_dump(start_time)


if __name__ == '__main__':
    t = threading.Thread(target=listen)
    t.start()
    now = datetime.datetime.now()
    threading.Timer(5.0, schedule_packet_dump, (now,)).start()
