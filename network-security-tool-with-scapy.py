#!/usr/bin/python3

# Script Name: Network Security Tool with Scapy
# Class Name: Ops 401
# Author Name: Carsten Rossen
# Date of Latest Revision: 4/21/21
# Purpose: Scans specified ports on a specified host.
# NOTE: Please run in sudo

# Import libraries

from scapy.all import ICMP, IP, sr1, TCP
import random
import ipaddress
import os
from arprequest import ArpRequest


# Declare functions

# Scan the ports of a host
def tcp_scanner(ip):
    # generate source port
    src_port = random.randint(1025, 65534)
    dst_ports = []

    # input destination ports
    while True:
        dst_ports.append(int(input("Please specify port to scan: ")))
        answer = input("Would you like to specify another port? (y/n): ")
        if answer != 'y':
            break

    # scan specified ports
    for port in dst_ports:
        response = sr1(
            IP(dst=ip)/TCP(sport=src_port,dport=port,flags="S"),timeout=1,
            verbose=0)

        if response is None:
            print(f"{ip}:{port} is filtered (silently dropped).")

        elif(response.haslayer(TCP)):
            if(response.getlayer(TCP).flags == 0x12):
                send_rst = sr(
                    IP(dst=ip)/TCP(sport=src_port,dport=port,flags='R'),
                    timeout=1,
                    verbose=0
                )
                print(f"{ip}:{port} is open.")
            elif (response.getlayer(TCP).flags == 0x14):
                print(f"{ip}:{port} is closed.")

        elif(response.haslayer(ICMP)):
            if(
                int(response.getlayer(ICMP).type) == 3 and 
                int(response.getlayer(ICMP).code) in [1,2,3,9,10,13]
            ):
                print(f"{ip}:{port} is filtered (silently dropped).")

# ping ip addresses on the network
def ping_sweep(network):
    index = 0
    active_count = 0
    for ip in network:
        if index != 0 and index != 1:
            ping_response = os.system("ping -c 1 " + str(ip))
            
            if ping_response == None:
                print("There was no response.")
            elif ping_response == 3:
                print("Host is actively blocking ICMP traffic.")
            else:
                print("Host is responding")
                active_count+=1

        index+=1
    
    print(f"There are {active_count} hosts online.")

# ARP request the hosts on the network
def arp(network):
    index = 0
    for ip in network:
        if index != 0 and index != 1:
            ar = ArpRequest(ip, 'eth0')
            active = ar.request()
            if active:
                tcp_scanner(ip)
        
        index+=1


# Main

# Menu system
print("Would you like to run this program in:")
print("   1. TCP Port Range Scanner Mode")
print("   2. ICMP Ping Sweep Mode")
print("   3. ARP Mode")
menu_choice = input("\nPlease specify choice (1/2/3): ")

if menu_choice == "1":
    ip = input("Please specify host IP address: ")
    tcp_scanner(ip)
elif menu_choice == "2" or menu_choice == "3":
    network_address = input("Please specify a network address: ")
    network = ipaddress.ip_network(network_address)
    if menu_choice == "2":
        ping_sweep(network)
    else:
        arp(network)
else:
    print("IMPROPER COMMAND. TERMINATING PROGRAM.")

# End