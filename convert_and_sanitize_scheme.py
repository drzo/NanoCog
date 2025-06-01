#!/usr/bin/env python3
"""
Convert and sanitize Scheme files for NanoCog training.

This script:
1. Finds all .scm files in the opencog-central directory
2. Converts them to .txt files with sanitized content
3. Removes or replaces problematic tokens/characters
4. Ensures the content is suitable for GPT training
"""

import os
import re
import glob
from pathlib import Path

def sanitize_text(text):
    """
    Sanitize text content by removing or replacing problematic tokens.
    """
    # Remove or replace the problematic <|endoftext|> token
    text = text.replace('<|endoftext|>', '')
    
    # Remove other potentially problematic special tokens
    # Common GPT special tokens that might cause issues
    special_tokens = [
        '<|startoftext|>',
        '<|endoftext|>',
        '<|im_start|>',
        '<|im_end|>',
        '<|pad|>',
        '<|eos|>',
        '<|bos|>',
        '<|unk|>',
    ]
    
    for token in special_tokens:
        text = text.replace(token, '')
    
    # Remove any remaining angle bracket tokens that look like special tokens
    text = re.sub(r'<\|[^>]*\|>', '', text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)  # Max 2 consecutive newlines
    text = re.sub(r'[ \t]+', ' ', text)  # Multiple spaces/tabs to single space
    
    # Remove any non-printable characters except common whitespace
    text = ''.join(char for char in text if char.isprintable() or char in '\n\t\r')
    
    # Ensure the text ends with a newline
    if text and not text.endswith('\n'):
        text += '\n'
    
    return text

def convert_scheme_file(scm_path, output_dir):
    """
    Convert a single Scheme file to a sanitized text file.
    """
    try:
        with open(scm_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Sanitize the content
        sanitized_content = sanitize_text(content)
        
        # Create output filename
        relative_path = os.path.relpath(scm_path, 'opencog-central')
        txt_path = os.path.join(output_dir, relative_path.replace('.scm', '.txt'))
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(txt_path), exist_ok=True)
        
        # Write the sanitized content
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(sanitized_content)
        
        return txt_path, len(sanitized_content)
    
    except Exception as e:
        print(f"Error processing {scm_path}: {e}")
        return None, 0

def main():
    """
    Main function to convert all Scheme files.
    """
    # Create output directory
    output_dir = 'data/opencog-scheme-txt'
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .scm files
    scm_files = glob.glob('opencog-central/**/*.scm', recursive=True)
    
    print(f"Found {len(scm_files)} Scheme files to convert")
    
    total_files = 0
    total_chars = 0
    failed_files = 0
    
    for scm_file in scm_files:
        result_path, char_count = convert_scheme_file(scm_file, output_dir)
        if result_path:
            total_files += 1
            total_chars += char_count
            if total_files % 50 == 0:
                print(f"Processed {total_files} files...")
        else:
            failed_files += 1
    
    print(f"\nConversion complete!")
    print(f"Successfully converted: {total_files} files")
    print(f"Failed conversions: {failed_files} files")
    print(f"Total characters: {total_chars:,}")
    print(f"Average file size: {total_chars // max(total_files, 1):,} characters")
    print(f"Output directory: {output_dir}")
    
    # Create a summary file
    summary_path = os.path.join(output_dir, 'conversion_summary.txt')
    with open(summary_path, 'w') as f:
        f.write(f"Scheme File Conversion Summary\n")
        f.write(f"==============================\n\n")
        f.write(f"Total .scm files found: {len(scm_files)}\n")
        f.write(f"Successfully converted: {total_files}\n")
        f.write(f"Failed conversions: {failed_files}\n")
        f.write(f"Total characters: {total_chars:,}\n")
        f.write(f"Average file size: {total_chars // max(total_files, 1):,} characters\n")
        f.write(f"Conversion date: {__import__('datetime').datetime.now()}\n")
    
    print(f"Summary written to: {summary_path}")

if __name__ == "__main__":
    main()
