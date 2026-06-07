import nmap

nm = nmap.PortScanner()

print("Escaneando red, por favor espera...")

# Ejecutamos el escaneo
nm.scan(hosts='192.168.40.0/24', arguments='-n -sP -PE -PA21,23,80,3389')

# Lista de hosts detectados
hosts_list = [(x, nm[x]['status']['state']) for x in nm.all_hosts()]

# Imprimimos los resultados
for host, status in hosts_list:
    print(f'{host} : {status}')
