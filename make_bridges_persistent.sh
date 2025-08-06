#!/bin/bash
# Script to make OpenNebula bridges persistent across reboots
# Creates a systemd service to recreate bridges on boot
# RUN THIS SCRIPT ON EACH COMPUTE NODE as root after creating bridges

echo "=== Making OpenNebula Bridges Persistent ==="
echo "Creating systemd service to recreate bridges on boot"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root"
    exit 1
fi

# Create the bridge recreation script
cat > /usr/local/bin/opennebula-bridges.sh << 'EOF'
#!/bin/bash
# OpenNebula Bridge Recreation Script
# Automatically recreates bridges on system boot

echo "OpenNebula: Creating bridges on boot..."

# Wait for network to be ready
sleep 10

# Check if kvm0 exists
if ! ip link show kvm0 >/dev/null 2>&1; then
    echo "OpenNebula: kvm0 interface not found, waiting..."
    sleep 30
fi

# Create bridges for VLANs 1-999
for i in {1..999}
do
    BRIDGE_NAME="br$i"
    VLAN_INTERFACE="kvm0.$i"
    
    # Skip if bridge already exists
    if brctl show | grep -q "^$BRIDGE_NAME"; then
        continue
    fi
    
    # Create VLAN interface
    ip link add link kvm0 name "$VLAN_INTERFACE" type vlan id "$i" 2>/dev/null
    
    # Create bridge
    brctl addbr "$BRIDGE_NAME" 2>/dev/null
    
    # Add VLAN interface to bridge
    brctl addif "$BRIDGE_NAME" "$VLAN_INTERFACE" 2>/dev/null
    
    # Bring interfaces up
    ip link set "$VLAN_INTERFACE" up 2>/dev/null
    ip link set "$BRIDGE_NAME" up 2>/dev/null
done

echo "OpenNebula: Bridge creation completed"
EOF

# Make the script executable
chmod +x /usr/local/bin/opennebula-bridges.sh

# Create systemd service
cat > /etc/systemd/system/opennebula-bridges.service << 'EOF'
[Unit]
Description=OpenNebula Bridge Creation Service
After=network.target
Wants=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/opennebula-bridges.sh
RemainAfterExit=yes
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable the service
systemctl daemon-reload
systemctl enable opennebula-bridges.service

echo "✅ Systemd service created and enabled"
echo ""
echo "Service details:"
echo "  Service file: /etc/systemd/system/opennebula-bridges.service"
echo "  Script file: /usr/local/bin/opennebula-bridges.sh"
echo ""
echo "To test the service:"
echo "  systemctl start opennebula-bridges.service"
echo "  systemctl status opennebula-bridges.service"
echo ""
echo "To check service logs:"
echo "  journalctl -u opennebula-bridges.service"
echo ""
echo "The bridges will now be recreated automatically on every boot!"
