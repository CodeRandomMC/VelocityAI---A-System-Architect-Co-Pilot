#!/usr/bin/env python3
"""
Test script to verify that the markdown sanitization function works correctly.
"""

import bleach

def sanitize_markdown_output(content: str) -> str:
    """
    Sanitize markdown content to prevent XSS attacks.
    
    This function removes potentially dangerous HTML tags and attributes
    while preserving safe markdown formatting.
    
    Args:
        content (str): The raw markdown content from LLM
        
    Returns:
        str: Sanitized markdown content safe for rendering
    """
    # Define allowed HTML tags for markdown formatting
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',  # Headers
        'p', 'br', 'hr',                       # Paragraphs and breaks
        'strong', 'b', 'em', 'i', 'u', 's',   # Text formatting
        'ul', 'ol', 'li',                      # Lists
        'blockquote', 'pre', 'code',           # Code and quotes
        'table', 'thead', 'tbody', 'tr', 'th', 'td',  # Tables
        'a',                                   # Links (with limited attributes)
    ]
    
    # Define allowed attributes for specific tags
    allowed_attributes = {
        'a': ['href', 'title'],
        'code': ['class'],  # For syntax highlighting
        'pre': ['class'],   # For code blocks
    }
    
    # Sanitize the content
    cleaned_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True  # Remove disallowed tags completely
    )
    
    # Additional protection: ensure URLs in links are safe
    cleaned_content = bleach.linkify(
        cleaned_content,
        callbacks=[bleach.callbacks.nofollow]  # Add rel="nofollow" to external links
    )
    
    return cleaned_content

def test_sanitization():
    """Test the sanitization function with various potentially malicious inputs."""
    
    print("Testing Markdown Sanitization...")
    print("=" * 50)
    
    # Test 1: Normal markdown should pass through
    normal_md = "## Test Header\n**Bold text** and *italic text*\n- List item\n"
    result1 = sanitize_markdown_output(normal_md)
    print("Test 1 - Normal Markdown:")
    print(f"Input:  {repr(normal_md)}")
    print(f"Output: {repr(result1)}")
    print()
    
    # Test 2: Script tag should be removed
    malicious_md = "## Heading\n<script>alert('XSS')</script>\nNormal text"
    result2 = sanitize_markdown_output(malicious_md)
    print("Test 2 - Script Tag (should be removed):")
    print(f"Input:  {repr(malicious_md)}")
    print(f"Output: {repr(result2)}")
    print()
    
    # Test 3: Onclick handler should be removed
    onclick_md = "## Heading\n<a href='#' onclick='alert(\"XSS\")'>Click me</a>"
    result3 = sanitize_markdown_output(onclick_md)
    print("Test 3 - Onclick Handler (should be removed):")
    print(f"Input:  {repr(onclick_md)}")
    print(f"Output: {repr(result3)}")
    print()
    
    # Test 4: Safe link should be preserved
    safe_link_md = "## Heading\n[Safe Link](https://example.com)"
    result4 = sanitize_markdown_output(safe_link_md)
    print("Test 4 - Safe Link (should be preserved):")
    print(f"Input:  {repr(safe_link_md)}")
    print(f"Output: {repr(result4)}")
    print()
    
    # Test 5: iframe should be removed
    iframe_md = "## Heading\n<iframe src='javascript:alert(\"XSS\")'></iframe>"
    result5 = sanitize_markdown_output(iframe_md)
    print("Test 5 - iframe (should be removed):")
    print(f"Input:  {repr(iframe_md)}")
    print(f"Output: {repr(result5)}")
    print()
    
    print("✅ Sanitization test completed!")

if __name__ == "__main__":
    test_sanitization()
