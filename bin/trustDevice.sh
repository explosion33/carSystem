#!/bin/bash
bluetoothctl << EOF
trust $1
exit
EOF
