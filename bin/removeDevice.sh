#!/bin/bash
bluetoothctl << EOF
remove $1
exit
EOF
