import time
import driver

client = driver.MessagingClient(username="test", password="test", topic="test/example")
client.connect()

for i in range(1000):
    client.send(str(i))
    message = client.read()
    if message is not None:
        print(message)
    time.sleep(1)
