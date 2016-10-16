# LatencyTester
Latency tester between an Androide device and a second device with auto answer enabled.

SW needs to execute on a Raspberry Pi since GPIO pins are used.
SW requires a sound card with 2-channel in and output (Phone A will use left channel and phone B right).
SW has been developed using Behringer UCA-222 USB sound card

Test description:
Test requires two phones (at least one needs to be Android phone). Each phone will be connected through a 4-pol 3.5 headphone connector to send and receive audio + emulating headphone PLAY button (microphone resistance decreased to 100 Ohm through controlling a relay using Raspberry GPIO pins)).
Test tool will perform instruct Android device connected to Phone A connector to call an entry in the phone book using voice recognition (sw emulates headset input by emulating headphone click through controlling a relay from Raspberry PI GPIO pins).
When the call is initiated then a sound will be played trough each phone. The sound played will be mixed into the audio recorded and used as reference (T=0 to avoid dealing with play out delay). The received sound from each phone is recorded on each phones channel (Left=A or Right=B). The SW will then measure the time between receiving the played sound and receiving the sound on the other phone.

Schematic HW layout:
To be added...
