import requests, json, time

BASE_URI = "http://localhost:58000/api/v1"
USERNAME = "admin"
PASSWORD = "admin123!"
SYSLOG_IP = "192.168.100.100"
NTP_IP = "192.168.100.100"

def get_ticket():
    headers = {"Content-Type": "application/json"}
    body = json.dumps({"username": USERNAME, "password": PASSWORD})
    r = requests.post(f"{BASE_URI}/ticket", data=body, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["response"]["serviceTicket"]

def list_devices(ticket):
    r = requests.get(f"{BASE_URI}/network-device", headers={"X-Auth-Token": ticket}, timeout=10)
    r.raise_for_status()
    for d in r.json()["response"]:
        print(f"{d['hostname']:<16}{d['serialNumber']:<14}{d['softwareVersion']}")

def set_syslog(ticket):
    payload = {"syslogServers": [{"ipAddress": SYSLOG_IP, "level": "debug"}]}
    h = {"X-Auth-Token": ticket, "Content-Type": "application/json"}
    r = requests.put(f"{BASE_URI}/wan/network-wide-setting", data=json.dumps(payload), headers=h, timeout=10)
    r.raise_for_status()
    print("Syslog configured")

def push_cli(ticket, device_id, commands):
    h = {"X-Auth-Token": ticket, "Content-Type": "application/json"}
    r = requests.post(f"{BASE_URI}/network-device/{device_id}/cli", data=json.dumps({"commands": commands}), headers=h, timeout=10)
    r.raise_for_status()

def configure_time(ticket):
    r = requests.get(f"{BASE_URI}/network-device", headers={"X-Auth-Token": ticket}, timeout=10)
    r.raise_for_status()
    ids = [d["id"] for d in r.json()["response"]]
    cmds = ["configure terminal", f"ntp server {NTP_IP}", "service timestamps log datetime msec", "end", "write"]
    for i in ids:
        push_cli(ticket, i, cmds)
    print("NTP and timestamps configured")

def main():
    t = get_ticket()
    print("Ticket:", t)
    list_devices(t)
    set_syslog(t)
    configure_time(t)

if __name__ == "__main__":
    main()