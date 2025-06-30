import nmap

class IOTNetworkScanner:
    def __init__(self, subnet):
        self.subnet = subnet
        self.scanner = nmap.PortScanner()
        # Remplacer le binaire utilisé par `sudo nmap`
        self.scanner.NMAP_SCAN_EXECUTABLE = 'sudo nmap'

        # Mapping statique des ports à des protocoles IoT spécifiques
        self.port_protocol_mapping = {
            1883: 'MQTT',
            4840: 'OPCUA',
            80: 'HTTP',
            443: 'HTTPS',
            5683: 'CoAP',
            5020: 'Modbus',
            5672: 'AMQP'
        }

    def scan_network(self):
        """
        Scan the network using nmap to identify devices and services.
        """
        print(f"Scanning the network in subnet {self.subnet}...")

        # Initialisation du dictionnaire final pour stocker les résultats
        results = []

        # Scan the subnet using nmap
        try:
            #self.scanner.scan(hosts=self.subnet, arguments='-p 1883,4840,80,443,5683,5020,5672')
            self.scanner.scan(
                hosts=self.subnet,
                arguments='--open -sT -sU -p T:1883,4840,80,443,5683,5020,5672,U:1883,4840,80,443,5683,5020,5672'
            )

            # Iterate over all hosts found and their respective open ports
            for host in self.scanner.all_hosts():
                if host.endswith('.1'):
                    continue  # On ignore l'ip de l'hote
                # Iterate through all protocols for the host
                for proto in self.scanner[host].all_protocols():
                    lport = self.scanner[host][proto].keys()
                    for port in lport:
                        # Map the port to an IoT protocol
                        protocol = self.port_protocol_mapping.get(port, 'Unknown IoT Protocol')
                        
                        # Ajouter les informations dans le dictionnaire
                        results.append({
                            'host': host,
                            'state': self.scanner[host].state(),
                            'port': port,
                            'protocol': protocol
                        })

        except Exception as e:
            print(f"Error during scan: {str(e)}")

        return results

    def run(self):
        return self.scan_network()

# Example usage
if __name__ == "__main__":
    scanner = IOTNetworkScanner("172.17.0.0/24")
    results = scanner.run()
    for entry in results:
        print(entry)
