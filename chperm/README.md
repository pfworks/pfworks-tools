# Custom chown Implementation with chmod Functionality

This is a hybrid implementation that combines `chown` and `chmod` functionality, written in C and based on the GNU coreutils source code. It can change both file ownership and permissions in a single command.

## Features

- Change file and directory ownership (user and/or group)
- Change file and directory permissions (numeric and symbolic modes)
- Support for both username/groupname and numeric UID/GID
- Recursive operation with `-R` flag
- Verbose output with `-v` flag
- Changes-only output with `-c` flag
- Quiet mode with `-f` flag
- Symbolic link handling with `-h` (no-dereference) and `-L` (dereference) flags

## Building

```bash
make
```

## Usage

```bash
./chperm [OPTION]... [OWNER][:[GROUP]] [MODE] FILE...
```

### Options

- `-c, --changes`: Report only when a change is made
- `-f, --silent, --quiet`: Suppress most error messages
- `-v, --verbose`: Output diagnostic for every file processed
- `-R, --recursive`: Operate on files and directories recursively
- `-h, --no-dereference`: Affect symbolic links instead of referenced files
- `-L, --dereference`: Dereference all symbolic links
- `--help`: Display help and exit
- `--version`: Output version information and exit

### Permission Modes

**Numeric modes (octal):**
- `755` - rwxr-xr-x (owner: read/write/execute, group/others: read/execute)
- `644` - rw-r--r-- (owner: read/write, group/others: read-only)
- `600` - rw------- (owner: read/write, group/others: no access)

**Symbolic modes:**
- `u+x` - Add execute permission for user (owner)
- `g-w` - Remove write permission for group
- `o=r` - Set others to read-only
- `a+rw` - Add read/write for all (user, group, others)
- `u+x,g-w,o=r` - Multiple operations separated by commas

### Examples

```bash
# Change owner only
./chperm root file.txt

# Change owner and group
./chperm root:staff file.txt

# Change owner and permissions
./chperm root 755 file.txt

# Change owner, group, and permissions
./chperm root:staff 644 file.txt

# Change only the group and permissions
./chperm :staff 755 file.txt

# Use symbolic permissions
./chperm root u+x,g-w file.txt

# Recursive change with verbose output
./chperm -R -v user:group 755 directory/

# Use numeric IDs with permissions
./chperm 1000:1000 644 file.txt

# Only change permissions (keep current owner)
./chperm $(whoami) u+x file.txt
```

## Testing

Run the built-in test suite:

```bash
make test
```

## Implementation Details

This hybrid implementation includes:

1. **Command-line parsing**: Uses `getopt_long()` for both short and long options
2. **User/group resolution**: Supports both names and numeric IDs using `getpwnam()` and `getgrnam()`
3. **Permission parsing**: 
   - Numeric modes parsed as octal (755, 644, etc.)
   - Symbolic modes supporting u/g/o/a with +/-/= and r/w/x
4. **Recursive directory traversal**: Manual implementation using `opendir()` and `readdir()`
5. **Symbolic link handling**: Uses `lstat()` and `lchown()` when appropriate
6. **Error handling**: Proper error reporting with `errno` and `strerror()`
7. **Verbose output**: Shows both ownership and permission changes in human-readable format

## Differences from Standard Tools

This hybrid version combines functionality that is normally split between `chown` and `chmod`:

**Advantages:**
- Single command for ownership and permission changes
- Consistent interface and options
- Atomic operations (both ownership and permissions changed together)

**Differences from GNU chown:**
- Adds permission-changing capability (non-standard)
- No `--reference` option
- No `--from` option for conditional changes
- No `--preserve-root` protection
- Simplified error handling
- No internationalization support

**Differences from GNU chmod:**
- Combined with ownership changing
- No `--reference` option
- Simplified symbolic mode parsing

## Files

- `chperm.c`: Main hybrid implementation
- `Makefile`: Build configuration with comprehensive tests
- `README.md`: This documentation
- `LICENSE': GNU v3 License

