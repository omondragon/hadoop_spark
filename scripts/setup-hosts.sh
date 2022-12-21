#!/bin/bash

echo "Creating hosts file"
cat > /etc/hosts <<EOF
192.168.200.3 nodemaster
192.168.200.4 node1
192.168.200.5 node2
EOF
