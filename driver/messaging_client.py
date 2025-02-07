import paho.mqtt.client as mqtt
import queue

__author__ = "Jonas Halbeisen"
__license__ = "http://www.apache.org/licenses/LICENSE-2.0"
__version__ = "1.0"

class MessagingClient:
    """
    Driver for MQTT client. 
    """

    host: str = "srems01.ost.ch"
    port: int = 1883
    messages: queue.Queue[str] = queue.Queue(maxsize=1024)
    _connected: bool = False

    def __init__(self, username: str, password: str, topic: str) -> None:
        """
        Create a new MQTT client. 
 
        Parameters
        ----------
        username : username under which this client connects to the server
        password : password
        topic : name of the topic, this topic is used for any further communication
        """
        self.topic = topic
        # Setup Client
        self.client = mqtt.Client(client_id=None, protocol=mqtt.MQTTv5)
        self.client.username_pw_set(username, password)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    def _on_connect(self, client: mqtt.Client, userdata, flags, rc, properties=None) -> None:
        options = mqtt.SubscribeOptions(qos=0, noLocal=True)
        self.client.subscribe(self.topic, options=options)
        self._connected = True

    def _on_disconnect(self, client: mqtt.Client, userdata, rc, properties=None) -> None:
        self._connected = False

    def _on_message(self, client: mqtt.Client, userdata, msg: mqtt.MQTTMessage) -> None:
        if str(msg.topic) == self.topic:
            if not self.messages.full():
                self.messages.put(msg.payload.decode('utf-8'))

    def connect(self) -> None:
        """
        Connects to a server. 
 
        Returns
        -------
        None
        """
        self.client.connect(self.host, self.port, clean_start=True)
        self.client.loop_start()
        while not self._connected:
            pass

    def disconnect(self) -> None:
        """
        Disconnects from a server. 
 
        Returns
        -------
        None
        """
        self.client.disconnect()

    def send(self, message: str) -> None:
        """
        Writes a message under the fixed topic of this client. 
        
        Parameters
        ----------
        message : message to send

        Returns
        -------
        None
        """
        self.client.publish(self.topic, payload=message, qos=0, retain=False)

    def read(self) -> str | None:
        """
        Reads from a topic. 
 
        Returns
        -------
        message or None
        """
        try:
            return self.messages.get_nowait()
        except queue.Empty:
            return None

    def is_connected(self) -> bool:
        """
        Checks if client is connected to a server. 
 
        Returns
        -------
        True if connected
        """
        return self._connected