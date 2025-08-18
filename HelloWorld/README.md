# Hello World Code Generator

A cross-platform GUI application that generates "Hello World" code in over 50 programming languages.

## Features

- **Cross-platform compatibility**: Works on Windows, macOS, and Linux
- **50+ programming languages** supported including Python, JavaScript, Java, C++, Go, Rust, and many more
- **Custom text input**: Generate code with any custom message, not just "Hello World!"
- **Easy-to-use interface**: Simple point-and-click operation
- **Code copying**: One-click copy to clipboard functionality
- **Syntax highlighting ready**: Generated code is properly formatted

## Supported Languages

The application supports code generation for over 70 programming languages and variants, organized in categories:

**BASIC Variants (22 dialects):**
- Classic 8-bit: Atari BASIC, Commodore BASIC, Apple BASIC, Sinclair BASIC
- Microsoft family: GW-BASIC, QBasic, QuickBASIC, BASICA
- Modern: FreeBASIC, PureBASIC, True BASIC, PowerBASIC
- Specialized: TI-BASIC, BBC BASIC, Liberty BASIC, REALbasic/Xojo, and more

**C Standards:**
- K&R C, C89/C90 (ANSI C), C99, C11, C17/C18, C23

**Fortran Standards:**
- FORTRAN 66, FORTRAN 77, Fortran 90, Fortran 95, Fortran 2003, Fortran 2008, Fortran 2018

**Popular Languages:**
- Python, JavaScript, Java, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin

**Functional Languages:**
- Haskell, Clojure, F#, Erlang, Elixir, OCaml, Scheme, Common Lisp

**Systems Languages:**
- Assembly (x86-64), D, Nim, Zig, Crystal, Oberon, Modula-2

**Web Technologies:**
- HTML, CSS, TypeScript, CoffeeScript, Elm, PureScript

**Scientific/Mathematical:**
- R, MATLAB, Julia

**Legacy/Specialized:**
- COBOL, Pascal, Ada, Smalltalk, Prolog, VHDL, Verilog

**And many more!**

## Requirements

- Python 3.6 or higher
- tkinter (included with most Python installations)

## Installation & Usage

### Option 1: Direct execution
```bash
# Make the script executable (Linux/macOS)
chmod +x hello_world_generator.py

# Run the application
python3 hello_world_generator.py
```

### Option 2: Using Python module
```bash
python -m hello_world_generator
```

## How to Use

1. **Launch the application** by running the Python script
2. **Select a programming language** from the list on the left
3. **Enter custom text** (optional) in the text field, or use the default "Hello World!"
4. **View the generated code** in the code area on the right
5. **Copy the code** using the "Copy Code" button
6. **Clear the code area** using the "Clear" button if needed

## Platform-Specific Notes

### Windows
- Python usually comes with tkinter pre-installed
- Run with: `python hello_world_generator.py`

### macOS
- Python 3 may need to be installed via Homebrew or python.org
- tkinter is included with official Python installations
- Run with: `python3 hello_world_generator.py`

### Linux
- Install tkinter if not available: `sudo apt-get install python3-tk` (Ubuntu/Debian)
- Or: `sudo yum install tkinter` (CentOS/RHEL)
- Run with: `python3 hello_world_generator.py`

## Features in Detail

### Custom Text Input
- Enter any text you want in the "Custom Text" field
- The application will generate code that prints your custom message
- Special characters are automatically escaped for proper syntax

### Code Generation
- Instant code generation as you select languages
- Proper syntax highlighting-ready formatting
- Includes necessary imports, headers, and boilerplate code

### User Interface
- Resizable window with minimum size constraints
- Scrollable language list and code area
- Status bar showing current operation status
- Professional, clean interface design

## Troubleshooting

### "tkinter not found" error
- **Linux**: Install python3-tk package
- **Windows**: Reinstall Python with tkinter option checked
- **macOS**: Use official Python installer from python.org

### Window doesn't appear
- Check if Python is properly installed
- Ensure you're using Python 3.6+
- Try running with `python3` instead of `python`

### Code not generating
- Make sure you've selected a language from the list
- Check the status bar for error messages
- Try clearing and regenerating the code

## Contributing

Feel free to add more programming languages or improve the existing code templates. The language definitions are stored in the `self.languages` dictionary in the `HelloWorldGenerator` class.

## License

This project is open source and available under the MIT License.
