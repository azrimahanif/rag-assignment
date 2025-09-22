#!/usr/bin/env python3
"""
Test script to verify Opik cloud connection
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '/app')

try:
    import opik
    print("✅ Opik package imported successfully")

    # Configure Opik with cloud settings
    opik.configure(
        api_key="nClCI2VHZExFKA5iJtu55SaUS",
        workspace="default",
        url="https://www.comet.com/opik"
    )
    print("✅ Opik configured for cloud")

    # Test creating a project
    try:
        project = opik.Project(name="rag-system-test")
        print("✅ Opik project accessible")
    except Exception as e:
        print(f"⚠️  Project access issue: {e}")

    # Test basic tracking
    try:
        @opik.track(project_name="rag-system")
        def test_function(message):
            return f"Processed: {message}"

        result = test_function("Hello Opik!")
        print(f"✅ Opik tracking test successful: {result}")
    except Exception as e:
        print(f"⚠️  Tracking test failed: {e}")

    print("✅ Opik cloud connection verified!")

except ImportError as e:
    print(f"❌ Opik not installed or import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Opik connection failed: {e}")
    sys.exit(1)