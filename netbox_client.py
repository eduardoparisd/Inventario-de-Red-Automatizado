
import requests
from config import NETBOX_URL, NETBOX_TOKEN

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Host": "netboxlab.dokploy.local"
}

def get_or_create_device(mac, hostname):
    nombre = hostname if hostname else mac
    url = f"{NETBOX_URL}/api/dcim/devices/"
    params = {"cf_mac_address": mac} if mac else {"name": nombre}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if data["count"] > 0:
        device = data["results"][0]
        print(f"Dispositivo existente: {device['name']} (ID: {device['id']})")
        return device["id"]

    payload = {
        "name": nombre,
        "device_type": {"slug": "dispositivo-generico"},
        "role": {"slug": "dispositivo-de-red"},
        "site": {"slug": "homelab"},
        "status": "active",
        "custom_fields": {"mac_address": mac}
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    device = response.json()
    if "name" not in device:
        print(f"Error creando dispositivo: {device}")
        return None
    print(f"Dispositivo creado: {device['name']} (ID: {device['id']})")
    return device["id"]

def update_device_ip(device_id, ip):
    if device_id is None:
        return
    
    interface_id = get_or_create_interface(device_id)

    url = f"{NETBOX_URL}/api/ipam/ip-addresses/"
    params = {"address": f"{ip}/24"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        print(f"Error {response.status_code} consultando IP: {response.text}")
        return
    data = response.json()

    if data["count"] > 0:
        ip_id = data["results"][0]["id"]
        ip_url = f"{NETBOX_URL}/api/ipam/ip-addresses/{ip_id}/"
        payload = {
            "assigned_object_type": "dcim.interface", 
            "assigned_object_id": interface_id
        }
        requests.patch(ip_url, headers=HEADERS, json=payload)
        print(f"IP {ip} actualizada a interfaz de dispositivo ID {device_id}")
    else:
        payload = {
            "address": f"{ip}/24",
            "status": "active",
            "assigned_object_type": "dcim.interface",
            "assigned_object_id": interface_id
        }
        requests.post(url, headers=HEADERS, json=payload)
        print(f"IP {ip} creada y asignada a dispositivo ID {device_id}")

def register_ip(ip, status):
    url = f"{NETBOX_URL}/api/ipam/ip-addresses/"
    params = {"address": f"{ip}/24"}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if data["count"] > 0:
        print(f"IP {ip} ya registrada, omitiendo")
        return

    payload = {
        "address": f"{ip}/24",
        "status": status
    }
    requests.post(url, headers=HEADERS, json=payload)
    print(f"IP {ip} registrada con status: {status}")

def get_all_ips_in_prefix(prefix):
    url = f"{NETBOX_URL}/api/ipam/ip-addresses/"
    params = {"parent": prefix}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    ips_registradas = []
    for ip_obj in data["results"]:
        ips_registradas.append(ip_obj["address"].split("/")[0])
    return ips_registradas

def get_or_create_interface(device_id):
    url = f"{NETBOX_URL}/api/dcim/interfaces/"
    params = {"device_id": device_id, "name": "Management"}
    response = requests.get(url, headers=HEADERS, params=params)
    data = response.json()

    if data["count"] > 0:
        return data["results"][0]["id"]

    payload = {
        "device": device_id,
        "name": "Management",
        "type": "virtual"
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    interface = response.json()
    if "id" not in interface:
        print(f"Error creando interfaz: {interface}")
        return None
    return interface["id"]

def set_primary_ip(device_id, ip):
    url = f"{NETBOX_URL}/api/ipam/ip-addresses/"
    params = {"address": f"{ip}/24"}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code != 200:
        return
    data = response.json()
    if data["count"] == 0:
        return

    ip_id = data["results"][0]["id"]
    device_url = f"{NETBOX_URL}/api/dcim/devices/{device_id}/"
    payload = {"primary_ip4": ip_id}
    requests.patch(device_url, headers=HEADERS, json=payload)
    print(f"IP primaria {ip} asignada al dispositivo ID {device_id}")