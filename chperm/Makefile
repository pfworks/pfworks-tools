CC = gcc
CFLAGS = -Wall -Wextra -std=c99 -O2
TARGET = chperm
SOURCE = chperm.c

.PHONY: all clean install test

all: $(TARGET)

$(TARGET): $(SOURCE)
	$(CC) $(CFLAGS) -o $(TARGET) $(SOURCE)

clean:
	rm -f $(TARGET)

install: $(TARGET)
	sudo cp $(TARGET) /usr/local/bin/
	sudo chmod 755 /usr/local/bin/$(TARGET)

test: $(TARGET)
	@echo "Testing basic functionality..."
	@echo "Creating test files..."
	@mkdir -p test_dir
	@touch test_dir/test_file1 test_dir/test_file2
	@mkdir -p test_dir/subdir
	@touch test_dir/subdir/test_file3
	@echo "Running tests..."
	@echo "1. Test verbose mode (ownership only):"
	./$(TARGET) -v $(USER) test_dir/test_file1
	@echo "2. Test ownership + permissions:"
	./$(TARGET) -v $(USER) 644 test_dir/test_file1
	@echo "3. Test symbolic permissions:"
	./$(TARGET) -v $(USER) u+x test_dir/test_file2
	@echo "4. Test recursive mode with permissions:"
	./$(TARGET) -R -v $(USER) 755 test_dir
	@echo "5. Test changes-only mode:"
	./$(TARGET) -c $(USER) 644 test_dir/test_file2
	@echo "6. Test group-only change with permissions:"
	./$(TARGET) -c :$(USER) u-x test_dir/test_file1
	@echo "Tests completed. Cleaning up..."
	@rm -rf test_dir

help:
	@echo "Available targets:"
	@echo "  all     - Build the program"
	@echo "  clean   - Remove built files"
	@echo "  install - Install to /usr/local/bin (requires sudo)"
	@echo "  test    - Run basic functionality tests"
	@echo "  help    - Show this help message"
