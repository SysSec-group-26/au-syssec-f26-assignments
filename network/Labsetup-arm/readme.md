# Mini TLS VPN Experiment

This folder contains a small VPN experiment with four containers:

- `client-10.9.0.5`: VPN client
- `server-router`: VPN server/router
- `host-192.168.60.5`: internal host 1
- `host-192.168.60.6`: internal host 2

The VPN tunnel runs automatically when the `VPN_Client` and `Router` services start. The client and router use the scripts in `/volumes`:

- `tun_client.py`
- `tun_server.py`
- `chat-listen.sh`
- `chat-connect.sh`

## 1. Start the experiment

From this directory:

```bash
cd network/Labsetup-arm
docker compose up -d
```

Check that the containers are running:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

You should see at least:

- `client-10.9.0.5`
- `server-router`
- `host-192.168.60.5`
- `host-192.168.60.6`

## 2. Verify the VPN tunnel is up

Watch the VPN logs in two terminals.

Terminal 1:

```bash
docker logs server-router -f
```

Terminal 2:

```bash
docker logs client-10.9.0.5 -f
```

If the tunnel is up, the client log should contain:

```text
TLS connection successul
```

The server log should contain:

```text
Listening on TLS 0.0.0.0:9090
```

## 3. Test connectivity through the tunnel

Run a ping from the VPN client to an internal host:

```bash
docker exec client-10.9.0.5 ping -c 4 192.168.60.5
```

Expected result:

- replies from `192.168.60.5`
- packet activity printed in the client and server logs

The packet logs mean:

- `From tun ==>`: a packet entered the tunnel logic from the TUN interface
- `From TLS <==`: a packet arrived over the TLS connection

## 4. Send messages between the containers

Use the helper chat scripts stored in `/volumes`.

### Listener on Host1

Open one terminal:

```bash
docker exec -it host-192.168.60.5 bash -lc 'cd /volumes && bash chat-listen.sh 9000 Host1'
```

### Connector on the VPN client

Open a second terminal:

```bash
docker exec -it client-10.9.0.5 bash -lc 'cd /volumes && bash chat-connect.sh 192.168.60.5 9000 VPN-Client'
```

Now type messages in either terminal. Each message is tagged with a timestamp and sender name.

## 5. Useful checks

Check routing on the VPN client:

```bash
docker exec client-10.9.0.5 ip route
```

Check that the tunnel scripts are running:

```bash
docker exec client-10.9.0.5 ps aux | grep tun_client.py
docker exec server-router ps aux | grep tun_server.py
```

## 6. Stop the experiment

```bash
docker compose down
```

If you want to remove the custom networks as well:

```bash
docker compose down --remove-orphans
```

## 8. Quick run sequence

If you just want the shortest path:

```bash
cd network/Labsetup-arm
docker compose up -d
docker exec client-10.9.0.5 ping -c 4 192.168.60.5
docker exec -it host-192.168.60.5 bash -lc 'cd /volumes && bash chat-listen.sh 9000 Host1'
docker exec -it client-10.9.0.5 bash -lc 'cd /volumes && bash chat-connect.sh 192.168.60.5 9000 VPN-Client'
```