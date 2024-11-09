# Experimental thingie for interfacing with Digital Norway's TC/2 loom

Using the MQTT internet-of-things protocol.

To run with [poetry](https://python-poetry.org/), first change into
the folder and run `poetry install`. Then start the server with

```
poetry run python3 tc2/mqtt.py --password yourmqttpasswordgoeshere
```

If you aren't our friends using our
[mosquitto](https://mosquitto.org/) instance on slab.org, then --host,
--port and --username options are also available to use your own or a
public mqtt broker.

If you manage to get this working, please [let us
know](mailto:alex@slab.org]!
