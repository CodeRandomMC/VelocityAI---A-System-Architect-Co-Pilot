"""
Test script to verify the refactored application works correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        import config
        print("✓ Config module imported successfully")
        
        import core_logic
        print("✓ Core logic module imported successfully")
        
        import llm_clients
        print("✓ LLM clients module imported successfully")
        
        import ui_components
        print("✓ UI components module imported successfully")
        
        import main
        print("✓ Main module imported successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_core_logic():
    """Test core logic functions."""
    try:
        from core_logic import validate_input, EXAMPLE_PLAN, ARCHITECT_SYSTEM_PROMPT
        
        # Test input validation
        assert validate_input("# Test plan") == True
        assert validate_input("") == False
        assert validate_input("   ") == False
        print("✓ Input validation works correctly")
        
        # Test example plan exists
        assert EXAMPLE_PLAN and len(EXAMPLE_PLAN) > 0
        print("✓ Example plan is available")
        
        # Test system prompt exists
        assert ARCHITECT_SYSTEM_PROMPT and len(ARCHITECT_SYSTEM_PROMPT) > 0
        print("✓ System prompt is available")
        
        return True
    except Exception as e:
        print(f"✗ Core logic test error: {e}")
        return False

def test_llm_clients():
    """Test LLM client creation."""
    try:
        from llm_clients import LLMClientFactory
        
        # Test Google client creation
        google_client = LLMClientFactory.create_google_client()
        print("✓ Google client created successfully")
        
        # Test LM Studio client creation
        lm_studio_client = LLMClientFactory.create_lm_studio_client()
        print("✓ LM Studio client created successfully")
        
        return True
    except Exception as e:
        print(f"✗ LLM clients test error: {e}")
        return False

def test_ui_components():
    """Test UI components creation."""
    try:
        from ui_components import UIComponents, create_gradio_interface
        
        # Test UI components creation
        ui = UIComponents()
        print("✓ UI components created successfully")
        
        # Test Gradio interface creation
        interface = create_gradio_interface()
        print("✓ Gradio interface created successfully")
        
        return True
    except Exception as e:
        print(f"✗ UI components test error: {e}")
        return False

def test_main_app():
    """Test main application creation."""
    try:
        from main import ArchitectureAnalyzer
        
        # Test application creation
        app = ArchitectureAnalyzer()
        print("✓ Architecture analyzer created successfully")
        
        return True
    except Exception as e:
        print(f"✗ Main app test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Running refactored application tests...\n")
    
    tests = [
        ("Import Tests", test_imports),
        ("Core Logic Tests", test_core_logic),
        ("LLM Clients Tests", test_llm_clients),
        ("UI Components Tests", test_ui_components),
        ("Main Application Tests", test_main_app)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The refactored application is working correctly.")
        print("\n▶️  To run the application, use: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
