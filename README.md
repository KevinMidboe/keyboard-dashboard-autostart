# keyboard-dashboard-autostart
Listens for keyboard events on function keys to launch programs

## Run

```bash
python3 main.py
```

### Options

```bash
python3 main.py --help

Available key bindings:

F16: openBrowser()
F17: openTerminal('watch -n 1 "sensors | grep temp1"')
```

## Configure environment

Bash:

```bash
virtualenv env
source env/bin/activate
```

Fish:

```bash
virtualenv env
source env/bin/activate.fish
```

## Requirements

Install system packages:

```bash
(sudo) apt install jq xdotool
```

Install python dependencies:

```bash
pip3 install -r requirements.txt
```

## Setup systemd service

Copy the systemd template & activate it:

```bash
(sudo) cp templates/keyboard-autostart.service /etc/systemd/system/
(sudo) systemctl enable keyboard-autostart.service
(sudo) systemctl start keyboard-autostart.service
```

### View application logs

```
(sudo) journalctl -u keyboard-autostart.service
```
