# Report the state of capture devices to Home Assistant

Use this script to inform Home Assistant if a capture device is active.
I'm using that to mute my Amazon Echo microphone while on a call.

## Installation

```bash
git clone https://github.com/saz/mic2ha.gitt
cd mic2ha
pip3 install --user -r requirements.txt
```

## Configuration

You can use parameters and environment variables.

```bash
Usage: mic2ha.py [OPTIONS]

Options:
  --webhook-url TEXT  Home Assistant webhook URL  [required]
  --entity-id TEXT    Home Assistant entity-id, e.g. input_boolean.some_name
                      [required]

  --ssid TEXT         Only send reports, if connected to this ssid
  --help              Show this message and exit.
```

Valid environment variables

```bash
WEBHOOK_URL
ENTITY_ID
SSID
```

Setting an SSID is optional.

If set, the script will check if your system is connected to the specified SSID and
only if it's connected, will report the state of your microphone to Home Assistant.

For more information on how to setup a webhook within Home Assistant, see\
https://www.home-assistant.io/docs/automation/trigger/#webhook-trigger

## Running with systemd

Use a systemd user unit to start this script at boot

```bash
mkdir -p ~/.config/systemd/user
cp mic2ha.service.example ~/.config/systemd/user/mic2ha.service
```

Before starting it, edit `~/.config/systemd/user/mic2ha.service` and configure your webhook url, entity-id and, if wanted, SSID. Do not forget to set the proper path to mic2ha.py

After that, you can start mic2ha:

```bash
systemctl --user enable mic2ha.service
systemctl --user start mic2ha.service
```

Try to make a call using e.g. https://meet.jit.si/mic2ha and see if it gets reported to Home Assistant properly.