## How ICMP works
ICMP is a protocol over IP that is usually whitelisted to allow debugging

## Modelling a Scenario that uses ICMP for exfoliation

Let's say we have two services `general-sender` and `icmp-sender`. Both of them run their packets through the service `proxy`, which is set up to filter any other traffic that is not over `icmp`. 
On "outside", we have two listening services: `general-listener` and `icmp-listener`. 
`general-listener` listens for `UDP` packets from `general-sender`, and
`icmp-listener` listens for `ICMP` packets from `icmp-sender`. 

The expected behaviour is, of course, that `general-listener` will fail to connect and accept packets from `general-sender`, while the `icmp` listener-sender pair will succeed.

# How to run
Step-by-step instructions on how to run the code with and without docker. 
Two terminals will be used.

## Running outside Docker
If you just want establish a one-way connection between two servers on localhost, do the following from `task1` directory:
1. Install the required python packages:
```
pip install -r requirements.txt
```
2. From the first terminal, run with sudo:
```
sudo python outside-listener/outside_listener.py 127.0.0.1
```
This will start a process that listens for messages on port 127.0.0.1
3. From the second terminal, run with sudo:
```
sudo python icmp-sender/icmp_sender.py 127.0.0.1
```
This will start a process that waits for you to input a message, which then is encrypted and sent to the listener. You will see your message popping up in the first terminal.

## Running within Docker

Here, we try to simulate a real world exfoliation scenario where we have a service within an enclosed network that manages to send messages outside of it. 

We will work with two networks: one that is internal and does not allow any communication with the outside world (except ICMP) called `internal-net`, and another one that represents the outside world `external-net`.
Inside `internal-net`, we 


```
iptables -I DOCKER-USER -p icmp -j ACCEPT
iptables -I DOCKER-USER -i internal-net -j DROP
```

### Trying to make connection through TCP
From `task1` directory, in the first terminal, run:
```
docker compose up --build
```

In the second terminal, try running `general-sender`:
```
docker compose run general-sender
```
As you can see, we get an error. This is a proof that the proxy is filtering `UDP` packets.

### Connect through ICMP
From `task1` directory, in the first terminal, run:
```
docker compose up --build
```
In the second terminal, run:
```
docker compose run icmp-sender
```
This will run a loop that awaits your message in the terminal:
```
Enter the message: 
```
just type your message and see how it appears in the first terminal as being printed by `outside-listener`.