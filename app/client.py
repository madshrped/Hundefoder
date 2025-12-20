import socket


class msg_reciver:
    def __init__(self):
        pass


esp32_ip = "192.168.1.85"
esp32_port = 8382

no_contact = (
    "Det var ikke muligt, at skabe kontakt :(\nÅben og luk app'en for at prøve igen"
)


class bridge:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.events = []
        self.send_event = lambda succes, message: f"{succes} to send {message}"
        self.recived_event = lambda message: f"recived: {message}"

    def add_event(self, event):
        self.events.append(event)

    def send_message(self, message: str, ip: str = esp32_ip, port: int = esp32_port):
        try:
            self.sock.sendto(message.encode(), (ip, port))
        except socket.timeout:
            print("No response from ESP32.")

    class reciver:
        def __init__(self, parent):
            self.parent = parent
            self.recived = []

        def add_recived(self, recived: str):
            self.recived.append(recived)

        def anticipate(self, timeout):
            try:
                self.parent.sock.settimeout(timeout)
                data, server = self.parent.sock.recvfrom(1024)
                print(data)
                self.add_recived(data.decode())
                self.parent.add_event(self.parent.recived_event(data.decode()))
                return data.decode()
            except socket.timeout:
                return no_contact
