import re

# ciao/devices/{device_uuid}/datastreams/{key}
# device_uuid is Device.uuid (the public identifier - never the internal
# `id` primary key), key is Datastream.key.
VALUE_TOPIC_FILTER = "ciao/devices/+/datastreams/+"

_VALUE_TOPIC_RE = re.compile(
    r"^ciao/devices/(?P<device_uuid>[^/]+)/datastreams/(?P<key>[^/]+)$"
)


def build_value_topic(device_uuid: str, key: str) -> str:
    return f"ciao/devices/{device_uuid}/datastreams/{key}"


def parse_value_topic(topic: str) -> tuple[str, str] | None:
    match = _VALUE_TOPIC_RE.match(topic)
    if not match:
        return None
    return match.group("device_uuid"), match.group("key")
