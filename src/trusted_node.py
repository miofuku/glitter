class TrustedNode:
    def __init__(self, node_id, node_type, initial_ip):
        self.node_id = node_id  # Unique, non-changeable identifier
        self.node_type = node_type  # 'device' or 'contact'
        self.ip_address = initial_ip

    def update_ip(self, new_ip):
        self.ip_address = new_ip
