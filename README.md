# Experimental thingie for interfacing with Digital Norway's TC2 loom

The TC2 loom is a semi-automated loom created by Digital Norway. The loom has a simple network protocol for communicating with its windows-based front-end. This software replaces the windows front-end with a python library, so that the loom can be controlled using the standard MQTT internet-of-things protocol.

To run with [poetry](https://python-poetry.org/), first change into the folder and run `poetry install`. Then start the server with

```
poetry run python3 tc2/mqtt.py --password yourmqttpasswordgoeshere
```

If you aren't our friends using our
[mosquitto](https://mosquitto.org/) instance on slab.org, then --host,

--port and --username options are also available to use your own or a
public mqtt broker.

If you manage to get this working, please [let us
know](mailto:alex@slab.org)!

## Related work

* Shanel Wu, Xavier A Corr, Xi Gao, Sasha De Koninck, Robin Bowers, and Laura Devendorf. 2024. Loom Pedals: Retooling Jacquard Weaving for Improvisational Design Workflows. In Proceedings of the Eighteenth International Conference on Tangible, Embedded, and Embodied Interaction (TEI '24). Association for Computing Machinery, New York, NY, USA, Article 10, 1–16. https://doi.org/10.1145/3623509.3633358
* Lea Albaugh, Scott E. Hudson, Lining Yao, and Laura Devendorf. 2020. Investigating Underdetermination Through Interactive Computational Handweaving. In Proceedings of the 2020 ACM Designing Interactive Systems Conference (DIS '20). Association for Computing Machinery, New York, NY, USA, 1033–1046. https://doi.org/10.1145/3357236.3395538
