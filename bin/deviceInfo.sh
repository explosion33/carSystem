#!/bin/bash
filename=bin/info.txt
bluetoothctl << EOF > $filename
info
exit
EOF
