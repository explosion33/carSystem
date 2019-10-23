#!/bin/bash
filename=bin/devices.txt
bluetoothctl << EOF > $filename
devices
exit
EOF

