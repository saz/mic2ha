#!/usr/bin/env python3
import os
import re
import pyinotify
import requests
import click
from subprocess import check_output, CalledProcessError, DEVNULL


class EventHandler(pyinotify.ProcessEvent):
    def __init__(self, webhook, ssid, entity_id, pevent=None, **kwargs):
        self.webhook = webhook
        self.ssid = ssid
        self.entity_id = entity_id
        super().__init__(pevent, **kwargs)

    def _check_ssid(self):
        if not self.ssid:
            return True

        try:
            result = check_output(["iwconfig"], encoding="UTF-8", stderr=DEVNULL)
        except CalledProcessError as e:
            print(e)
            return False

        m = re.search(f'.*ESSID:"({self.ssid})"', result)
        if m:
            return True
        return False

    def get_entity_domain(self):
        return self.entity_id.split(".")[0]

    def _get_payload(self, maskname):
        if maskname == "IN_CLOSE_WRITE":
            action = "turn_off"
        elif maskname == "IN_OPEN":
            action = "turn_on"
        return {
            "service": self.get_entity_domain(),
            "entity_id": self.entity_id,
            "action": action,
        }

    def _notify_ha(self, payload):
        r = requests.post(self.webhook, json=payload)
        if r.status_code == requests.codes.ok:
            return "notified"
        return f"notify failed ({r.status_code}): {r.text}"

    def process_default(self, event):
        if not self._check_ssid():
            print("SSID {self.ssid} not connected, HomeAssistant notification skipped")
            return
        result = self._notify_ha(self._get_payload(event.maskname))
        print(
            f"Received {event.maskname} for path {event.path}, HomeAssistant {result}"
        )


@click.command()
@click.option(
    "--webhook-url",
    help="Home Assistant webhook URL",
    required=True,
    envvar="WEBHOOK_URL",
)
@click.option(
    "--entity-id",
    help="Home Assistant entity-id, e.g. input_boolean.some_name",
    required=True,
    envvar="ENTITY_ID",
)
@click.option(
    "--ssid",
    help="Only send reports, if connected to this ssid",
    default=False,
    envvar="SSID",
)
def main(webhook_url, entity_id, ssid):
    path = "/dev/snd/pcm*c"
    wm = pyinotify.WatchManager()
    wm.add_watch(
        path=path, mask=pyinotify.IN_OPEN | pyinotify.IN_CLOSE_WRITE, do_glob=True
    )
    eh = EventHandler(webhook=webhook_url, ssid=ssid, entity_id=entity_id)
    notifier = pyinotify.Notifier(wm, eh)
    print(f"Watching all items matching {path}")
    notifier.loop()


if __name__ == "__main__":
    main()
