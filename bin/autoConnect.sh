#!/bin/sh
bluetoothctl << EOF
connect $1
exit
EOF
