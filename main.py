import ipaddress
from config import NETWORK_RANGE
from scanner import scan_network
from netbox_client import get_or_create_device, update_device_ip, register_ip, get_all_ips_in_prefix, set_primary_ip

def main():
    print("=== Iniciando inventario de red ===\n")

    dispositivos_activos = scan_network(NETWORK_RANGE)
    ips_activas = [d["ip"] for d in dispositivos_activos]

    print(f"\nDispositivos encontrados: {len(dispositivos_activos)}\n")

    for dispositivo in dispositivos_activos:
        ip = dispositivo["ip"]
        mac = dispositivo["mac"]
        hostname = dispositivo["hostname"]

        print(f"Procesando {ip} ({mac})")
        device_id = get_or_create_device(mac, hostname)
        update_device_ip(device_id, ip)
        set_primary_ip(device_id, ip)

    print("\n=== Registrando todas las IPs del rango ===\n")

    ips_ya_registradas = get_all_ips_in_prefix(NETWORK_RANGE)
    red = ipaddress.IPv4Network(NETWORK_RANGE)

    for ip in red.hosts():
        ip_str = str(ip)
        if ip_str in ips_ya_registradas:
            continue
        if ip_str in ips_activas:
            register_ip(ip_str, "active")
        else:
            register_ip(ip_str, "available")

    print("\n=== Inventario completado ===")

if __name__ == "__main__":
    main()
