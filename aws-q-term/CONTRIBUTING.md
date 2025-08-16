# Contributing to HAL 9000 - System Interface

Thank you for your interest in contributing to the HAL 9000 System Interface project! This document provides guidelines and information for contributors.

## 🚀 Quick Start for Contributors

### Development Setup
```bash
# Clone the repository
git clone https://gitlab.com/your-username/hal9000-interface.git
cd hal9000-interface

# Install development dependencies
pip install -r requirements.txt

# Test the application
python3 hal_gui.py
```

### Testing Your Changes
```bash
# Run diagnostic tests
./test_hal.sh

# Test PIL functionality
python3 test_pil.py

# Test PIL-free version
python3 hal_gui_no_pil.py

# Build package
make clean && make package
```

## 📋 How to Contribute

### 1. Reporting Issues
- **Bug Reports**: Use GitLab Issues with the `bug` label
- **Feature Requests**: Use GitLab Issues with the `enhancement` label
- **Documentation**: Use GitLab Issues with the `documentation` label

#### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.8.10]
- HAL version: [e.g. 2.0.0]
- PIL status: [Available/Not Available]

**Additional context**
Any other context about the problem.
```

### 2. Code Contributions

#### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes
4. **Test** thoroughly
5. **Commit** with clear messages
6. **Push** to your fork
7. **Create** a Merge Request

#### Branch Naming
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring

#### Commit Messages
Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
```
feat(ui): add amber color theme toggle
fix(shell): resolve tab completion for paths with spaces
docs(readme): update installation instructions
refactor(fonts): improve font selection system
```

### 3. Code Standards

#### Python Style
- Follow **PEP 8** style guidelines
- Use **4 spaces** for indentation
- **Maximum line length**: 100 characters
- Use **descriptive variable names**
- Add **docstrings** for functions and classes

#### Code Structure
```python
def function_name(param1, param2):
    """
    Brief description of function.
    
    Args:
        param1 (type): Description of param1
        param2 (type): Description of param2
    
    Returns:
        type: Description of return value
    """
    # Implementation
    return result
```

#### GUI Guidelines
- Use **consistent styling** with HAL theme
- Follow **existing color schemes**
- Maintain **responsive layout**
- Test with **both color themes**
- Ensure **accessibility**

### 4. Testing Requirements

#### Before Submitting
- [ ] Code runs without errors
- [ ] Both color themes work correctly
- [ ] Shell mode functions properly
- [ ] Tab completion works
- [ ] Q CLI integration works (if available)
- [ ] PIL-free version works
- [ ] Package builds successfully

#### Test Commands
```bash
# Syntax validation
python3 -m py_compile hal_gui.py
python3 -m py_compile hal_gui_no_pil.py

# Functional testing
./test_hal.sh

# Package testing
make clean && make package
tar -xzf hal9000-interface-*.tar.gz
cd hal9000-interface-*
./install.sh
```

## 🎨 Design Guidelines

### HAL Aesthetic
- **Colors**: Red for HAL, green/amber for terminal
- **Fonts**: IBM-style monospace fonts
- **Layout**: Clean, retro computer interface
- **Animations**: Subtle, not distracting

### User Experience
- **Intuitive**: Clear button labels and functions
- **Responsive**: Fast response to user actions
- **Accessible**: Works with and without dependencies
- **Professional**: Movie-accurate HAL appearance

## 📚 Development Areas

### High Priority
- **Performance**: Optimize GUI responsiveness
- **Compatibility**: Support more operating systems
- **Error Handling**: Improve error messages
- **Documentation**: Expand user guides

### Medium Priority
- **Features**: Voice synthesis, command history
- **Themes**: Additional color schemes
- **Shell**: Advanced shell features
- **AWS Integration**: Enhanced Q CLI features

### Low Priority
- **Plugins**: Extensible architecture
- **Multi-session**: Multiple shell tabs
- **File Browser**: Integrated file management
- **Configuration**: Settings GUI

## 🔧 Technical Architecture

### File Structure
```
hal9000-interface/
├── hal_gui.py              # Main GUI (PIL support)
├── hal_gui_no_pil.py       # PIL-free version
├── hal_debug.py            # Debug version
├── assets/                 # Images and resources
├── install.sh              # Installer script
├── test_*.py               # Test utilities
└── docs/                   # Documentation
```

### Key Components
- **HALInterface**: Main GUI class
- **Color Themes**: Theme management system
- **Font System**: IBM font selection
- **Shell Integration**: Command execution
- **Q CLI Integration**: Amazon Q interface

### Adding New Features

#### New Color Theme
1. Add theme to `get_theme_colors()`
2. Update `toggle_color_theme()`
3. Test with all UI elements
4. Update documentation

#### New Shell Feature
1. Modify shell command processing
2. Update tab completion if needed
3. Test with various commands
4. Ensure cross-platform compatibility

## 📖 Resources

### Documentation
- [README.md](README.md) - Main project documentation
- [SHELL_MODE_GUIDE.md](SHELL_MODE_GUIDE.md) - Shell usage guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide

### External References
- [Amazon Q CLI Documentation](https://docs.aws.amazon.com/amazonq/)
- [tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [PIL/Pillow Documentation](https://pillow.readthedocs.io/)

## 🤝 Community

### Communication
- **Issues**: Use GitLab Issues for bugs and features
- **Discussions**: Use GitLab Discussions for questions
- **Email**: Contact maintainers for sensitive issues

### Code of Conduct
- Be **respectful** and **inclusive**
- **Help** others learn and contribute
- **Focus** on constructive feedback
- **Celebrate** diverse perspectives

## 🏆 Recognition

Contributors will be recognized in:
- **README.md** contributors section
- **CHANGELOG.md** for significant contributions
- **Release notes** for major features

Thank you for contributing to the HAL 9000 Interface project! 🚀

---

*"I'm sorry, Dave. I'm afraid I can't do that."*
*But you can help make this HAL even better!* 🤖
