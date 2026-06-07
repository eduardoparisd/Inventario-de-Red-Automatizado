import nmap

def scan_network(network_range):
    scanner = nmap.PortScanner()

    print(f"Escaneando red: {network_range}")
    scanner.scan(hosts=network_range, arguments="-sn", sudo=True)

    devices = []

    for host in scanner.all_hosts():
        addresses = scanner[host].get("addresses", {})
        
        device = {
            "ip": host,
            "mac": addresses.get("mac", ""),
            "hostname": scanner[host].hostname(),
            "status": scanner[host].state()
        }

        devices.append(device)

    return devices
    
