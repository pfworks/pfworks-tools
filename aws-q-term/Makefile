# HAL 9000 Interface Makefile

.PHONY: all install package clean run test help

# Default target
all: package

# Install HAL interface locally
install:
	@echo "Installing HAL 9000 Interface..."
	./install.sh

# Create distribution package
package:
	@echo "Creating distribution package..."
	./package.sh

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -rf hal9000-interface-*
	rm -f *.tar.gz *.sha256
	@echo "Clean complete."

# Run HAL interface directly (development)
run:
	@echo "Launching HAL interface..."
	./launch_hal.sh

# Test dependencies and requirements
test:
	@echo "Testing system requirements..."
	@python3 --version || (echo "Python 3 not found" && exit 1)
	@python3 -c "import tkinter" || (echo "tkinter not available" && exit 1)
	@python3 -c "import PIL" 2>/dev/null || echo "Warning: Pillow not installed"
	@command -v q >/dev/null 2>&1 || echo "Warning: Q CLI not found"
	@echo "Requirements check complete."

# Download HAL image only
image:
	@echo "Downloading HAL image..."
	./download_hal_image.sh

# Show help
help:
	@echo "HAL 9000 Interface Build System"
	@echo ""
	@echo "Available targets:"
	@echo "  install   - Install HAL interface locally"
	@echo "  package   - Create distribution package"
	@echo "  clean     - Remove build artifacts"
	@echo "  run       - Launch HAL interface directly"
	@echo "  test      - Check system requirements"
	@echo "  image     - Download HAL image only"
	@echo "  help      - Show this help message"
	@echo ""
	@echo "Quick start:"
	@echo "  make package  # Create distribution"
	@echo "  make install  # Install locally"
	@echo "  make run      # Launch interface"
