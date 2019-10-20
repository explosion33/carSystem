#!/bin/bash
filename=info.txt
bluetoothctl << EOF > $filename
info
exit
EOF
