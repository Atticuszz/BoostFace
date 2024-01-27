import psutil


class CloudSystemStats:
    """ Local system stats"""

    def __init__(self):
        self.last_net_io = psutil.net_io_counters()

    def get_cpu_usage(self):
        return psutil.cpu_percent()

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_network_throughput(self):
        net_io = psutil.net_io_counters()
        net_send = net_io.bytes_sent - self.last_net_io.bytes_sent
        net_recv = net_io.bytes_recv - self.last_net_io.bytes_recv
        self.last_net_io = net_io
        return net_send + net_recv


cloud_system_stats = CloudSystemStats()
