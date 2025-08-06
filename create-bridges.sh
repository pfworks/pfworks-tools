#!/bin/bash
# Recreate OpenNebula Networks with External DHCP
# This script removes all existing networks and recreates them with external DHCP configuration

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}"
}

print_success() {
    print_status $GREEN "✅ $1"
}

print_error() {
    print_status $RED "❌ $1"
}

print_warning() {
    print_status $YELLOW "⚠️  $1"
}

print_info() {
    print_status $BLUE "ℹ️  $1"
}

# Check if running as oneadmin or with proper ONE_AUTH
if [ -z "$ONE_AUTH" ] && [ "$USER" != "oneadmin" ]; then
    print_error "This script must be run as oneadmin or with ONE_AUTH set"
    print_info "Run as: sudo -u oneadmin $0"
    print_info "Or set: export ONE_AUTH=/var/lib/one/.one/one_auth"
    exit 1
fi

# Set ONE_AUTH if not set
if [ -z "$ONE_AUTH" ]; then
    export ONE_AUTH="/var/lib/one/.one/one_auth"
fi

# Generate network definitions programmatically
# VLAN 16 + VLANs 100-600 (502 total VLANs)
NETWORKS=()

# Add VLAN 16
NETWORKS+=("16:br16:vlan16:VLAN 16 with external DHCP")

# Add VLANs 100-600
for vlan_id in {100..600}; do
    if [ "$vlan_id" -eq 212 ]; then
        # Mark VLAN 212 as dummy
        NETWORKS+=("212:br212:vlan212:VLAN 212 - DUMMY (skipped)")
    else
        NETWORKS+=("$vlan_id:br$vlan_id:vlan$vlan_id:VLAN $vlan_id with external DHCP")
    fi
done

print_header "OpenNebula Network Recreation with External DHCP"
print_info "Date: $(date)"
print_info "User: $(whoami)"
print_info "ONE_AUTH: $ONE_AUTH"
print_info "Total VLANs to process: ${#NETWORKS[@]} (VLAN 16 + VLANs 100-600)"
echo

# Count networks to be created vs skipped
NETWORKS_TO_CREATE=0
NETWORKS_TO_SKIP=0
for network_def in "${NETWORKS[@]}"; do
    IFS=':' read -r vlan_id bridge_name network_name description <<< "$network_def"
    if [[ "$description" == *"DUMMY"* ]]; then
        ((NETWORKS_TO_SKIP++))
    else
        ((NETWORKS_TO_CREATE++))
    fi
done

# Confirmation prompt
print_warning "This script will:"
print_warning "1. DELETE ALL existing OpenNebula networks"
print_warning "2. Recreate $NETWORKS_TO_CREATE networks with external DHCP configuration"
print_warning "3. Skip $NETWORKS_TO_SKIP networks (marked as dummy)"
echo
print_info "Networks to be created:"
print_info "  - VLAN 16 (vlan16)"
print_info "  - VLANs 100-211 (112 networks)"
print_info "  - VLANs 213-600 (388 networks)"
print_warning "  - VLAN 212 (vlan212) - SKIPPED (dummy)"
print_info "  Total: $NETWORKS_TO_CREATE networks"
echo

read -p "Are you sure you want to proceed? (yes/no): " confirm
if [[ "$confirm" != "yes" ]]; then
    print_info "Operation cancelled"
    exit 0
fi

# Step 1: Backup existing networks
print_header "Backing Up Existing Networks"
BACKUP_DIR="/tmp/opennebula-network-backup-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

print_info "Creating backup directory: $BACKUP_DIR"

# Get list of existing networks
EXISTING_NETWORKS=$(onevnet list --no-header | awk '{print $1}')

if [ -n "$EXISTING_NETWORKS" ]; then
    for net_id in $EXISTING_NETWORKS; do
        print_info "Backing up network $net_id"
        onevnet show $net_id > "$BACKUP_DIR/network-$net_id.txt"
    done
    print_success "Backup completed: $BACKUP_DIR"
else
    print_info "No existing networks found to backup"
fi

# Step 2: Check for VMs using networks
print_header "Checking for VMs Using Networks"
RUNNING_VMS=$(onevm list --no-header | grep -E "runn|pend" | wc -l)

if [ "$RUNNING_VMS" -gt 0 ]; then
    print_error "Found $RUNNING_VMS running/pending VMs"
    print_error "Please stop all VMs before recreating networks"
    print_info "Running VMs:"
    onevm list | grep -E "runn|pend"
    exit 1
fi

print_success "No running VMs found - safe to proceed"

# Step 3: Delete existing networks
print_header "Deleting Existing Networks"

if [ -n "$EXISTING_NETWORKS" ]; then
    for net_id in $EXISTING_NETWORKS; do
        NET_NAME=$(onevnet show $net_id | grep "^NAME" | cut -d'"' -f2)
        print_info "Deleting network $net_id ($NET_NAME)"
        
        if onevnet delete $net_id; then
            print_success "Deleted network $net_id"
        else
            print_error "Failed to delete network $net_id"
        fi
    done
else
    print_info "No networks to delete"
fi

# Verify all networks are deleted
REMAINING_NETWORKS=$(onevnet list --no-header | wc -l)
if [ "$REMAINING_NETWORKS" -eq 0 ]; then
    print_success "All networks deleted successfully"
else
    print_warning "$REMAINING_NETWORKS networks still exist"
    onevnet list
fi

# Step 4: Create new networks with external DHCP
print_header "Creating Networks with External DHCP"

CREATED_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0

for network_def in "${NETWORKS[@]}"; do
    IFS=':' read -r vlan_id bridge_name network_name description <<< "$network_def"
    
    # Skip dummy networks
    if [[ "$description" == *"DUMMY"* ]]; then
        print_warning "Skipping VLAN $vlan_id ($network_name) - marked as dummy"
        ((SKIPPED_COUNT++))
        continue
    fi
    
    print_info "Creating network: $network_name (VLAN $vlan_id)"
    
    # Create network configuration file
    NETWORK_FILE="/tmp/network-$network_name.txt"
    cat > "$NETWORK_FILE" << EOF
NAME = "$network_name"
BRIDGE = "$bridge_name"
VLAN_ID = "$vlan_id"
VN_MAD = "bridge"
DHCP = "YES"
EXTERNAL_DHCP = "YES"
DESCRIPTION = "$description"
EOF
    
    # Create the network
    if onevnet create "$NETWORK_FILE" >/dev/null 2>&1; then
        # Get the new network ID
        NEW_NET_ID=$(onevnet list | grep "$network_name" | awk '{print $1}')
        print_success "Created network $network_name (ID: $NEW_NET_ID)"
        ((CREATED_COUNT++))
        
        # Verify external DHCP is enabled (only check every 50th network to avoid spam)
        if [ $((CREATED_COUNT % 50)) -eq 0 ] || [ "$CREATED_COUNT" -eq 1 ]; then
            if onevnet show $NEW_NET_ID | grep -q 'EXTERNAL_DHCP="YES"'; then
                print_success "External DHCP verified for $network_name"
            else
                print_error "External DHCP not properly configured for $network_name"
            fi
        fi
    else
        print_error "Failed to create network $network_name"
        ((FAILED_COUNT++))
    fi
    
    # Clean up temporary file
    rm -f "$NETWORK_FILE"
    
    # Progress indicator every 50 networks
    if [ $((CREATED_COUNT % 50)) -eq 0 ] && [ "$CREATED_COUNT" -gt 0 ]; then
        print_info "Progress: $CREATED_COUNT networks created..."
    fi
done

# Step 5: Verify final configuration
print_header "Final Network Configuration"

FINAL_COUNT=$(onevnet list --no-header | wc -l)
print_info "Total networks in OpenNebula: $FINAL_COUNT"

# Show sample of created networks
print_info "Sample of created networks:"
onevnet list | head -10

if [ "$FINAL_COUNT" -gt 10 ]; then
    print_info "... and $((FINAL_COUNT - 10)) more networks"
fi

# Step 6: Verify bridge requirements
print_header "Bridge Requirements Check"

print_warning "IMPORTANT: Ensure these bridges exist on ALL OpenNebula nodes:"
print_info "  - Frontend server"
print_info "  - All compute nodes"
echo
print_info "Required bridges:"
print_info "  - br16 (for VLAN 16)"
print_info "  - br100 through br600 (for VLANs 100-600, except br212)"
print_info "  Total bridges needed: $NETWORKS_TO_CREATE"
echo
print_info "Use bridge creation scripts to create missing bridges:"
print_info "  ./create-vlan<ID>.sh"
print_info "  ./make-vlan<ID>-persistent.sh"

# Summary
print_header "Recreation Summary"
print_success "Network recreation completed successfully"
print_info "Backup location: $BACKUP_DIR"
echo
print_info "Creation Results:"
print_success "  Networks created: $CREATED_COUNT"
print_warning "  Networks skipped: $SKIPPED_COUNT (dummy)"
if [ "$FAILED_COUNT" -gt 0 ]; then
    print_error "  Networks failed: $FAILED_COUNT"
else
    print_success "  Networks failed: $FAILED_COUNT"
fi
print_info "  Total processed: ${#NETWORKS[@]}"
echo

print_info "All networks configured with:"
print_info "  - DHCP = \"YES\""
print_info "  - EXTERNAL_DHCP = \"YES\""
print_info "  - VN_MAD = \"bridge\""

print_info "Next steps:"
print_info "1. Create bridges on all nodes for VLANs: 16, 100-211, 213-600"
print_info "2. Test DHCP functionality with: ./test-dhcp-simple.sh MAC BRIDGE"
print_info "3. Deploy VMs using terraform"

print_header "Recreation Completed"
print_success "All $CREATED_COUNT networks configured for external DHCP"

exit 0
