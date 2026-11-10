from scapy.all import sniff

print("Sniffing on vcan0...")
sniff(iface="vcan0", prn=lambda p: p.show(), store=False)
