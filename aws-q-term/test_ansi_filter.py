#!/usr/bin/env python3
"""
Test ANSI escape code filtering for HAL GUI
"""

import re

def test_ansi_filtering():
    """Test ANSI escape code filtering"""
    
    # ANSI escape code patterns
    ansi_escape_pattern = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    ansi_color_pattern = re.compile(r'\x1B\[[0-9;]*m')
    
    def filter_ansi_codes(text):
        """Remove ANSI escape codes from text"""
        if not text:
            return text
        
        # Remove all ANSI escape sequences
        clean_text = ansi_escape_pattern.sub('', text)
        
        # Also remove any remaining color codes that might have been missed
        clean_text = ansi_color_pattern.sub('', clean_text)
        
        return clean_text
    
    def clean_output_text(text):
        """Clean output text for GUI display"""
        if not text:
            return text
        
        # Filter ANSI codes first
        clean_text = filter_ansi_codes(text)
        
        # Remove carriage return sequences (but keep newlines)
        clean_text = re.sub(r'\r(?!\n)', '', clean_text)
        
        # Handle backspace sequences more carefully
        # Only remove actual backspace characters (\b) and the character before them
        while '\b' in clean_text:
            # Find backspace and remove it along with the previous character
            pos = clean_text.find('\b')
            if pos > 0:
                # Remove the character before backspace and the backspace itself
                clean_text = clean_text[:pos-1] + clean_text[pos+1:]
            else:
                # Just remove the backspace if it's at the beginning
                clean_text = clean_text[1:]
        
        # Clean up excessive whitespace but preserve intentional formatting
        lines = clean_text.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove trailing whitespace but preserve leading whitespace for indentation
            cleaned_line = line.rstrip()
            cleaned_lines.append(cleaned_line)
        
        return '\n'.join(cleaned_lines)
    
    # Test cases
    test_cases = [
        # Basic color codes
        ("\x1b[38;5;10mtest.asm\x1b[0m", "test.asm"),
        ("\x1b[31mred text\x1b[0m", "red text"),
        ("\x1b[1;32mbold green\x1b[0m", "bold green"),
        
        # Complex sequences
        ("\x1b[38;5;196m\x1b[1mBright Red Bold\x1b[0m", "Bright Red Bold"),
        ("\x1b[48;5;21m\x1b[38;5;15mWhite on Blue\x1b[0m", "White on Blue"),
        
        # Mixed content
        ("Normal text \x1b[31mred\x1b[0m more normal", "Normal text red more normal"),
        ("File: \x1b[38;5;10mtest.asm\x1b[0m Size: 1024", "File: test.asm Size: 1024"),
        
        # Cursor movement and other escape codes
        ("\x1b[2J\x1b[H\x1b[31mCleared screen\x1b[0m", "Cleared screen"),
        ("\x1b[K\x1b[32mLine cleared\x1b[0m", "Line cleared"),
        
        # Real-world examples
        ("total 24\n\x1b[0m\x1b[01;34mdir1\x1b[0m\n\x1b[01;32mfile.txt\x1b[0m", "total 24\ndir1\nfile.txt"),
        ("-rw-r--r-- 1 user user 1024 Aug 16 12:00 \x1b[38;5;10mtest.asm\x1b[0m", "-rw-r--r-- 1 user user 1024 Aug 16 12:00 test.asm"),
    ]
    
    print("ANSI Escape Code Filtering Test")
    print("=" * 40)
    
    all_passed = True
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = clean_output_text(input_text)
        passed = result == expected
        all_passed = all_passed and passed
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\nTest {i}: {status}")
        print(f"Input:    {repr(input_text)}")
        print(f"Expected: {repr(expected)}")
        print(f"Got:      {repr(result)}")
        
        if not passed:
            print(f"Diff:     Expected '{expected}' but got '{result}'")
    
    print(f"\n{'='*40}")
    if all_passed:
        print("✅ All tests passed! ANSI filtering is working correctly.")
    else:
        print("❌ Some tests failed. Check the filtering logic.")
    
    return all_passed

if __name__ == "__main__":
    test_ansi_filtering()
