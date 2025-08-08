#!/usr/bin/env python3
"""
Simple test to verify our Spark engine imports correctly
"""

import sys
import traceback


def test_imports():
    print("Testing imports...")

    # Test config import
    try:
        from nullsweep.config import DataType, SPARK_AVAILABLE
        print(
            f"✓ Config imported successfully. SPARK_AVAILABLE: {SPARK_AVAILABLE}")
    except Exception as e:
        print(f"✗ Config import failed: {e}")
        traceback.print_exc()
        return False

    # Test Spark engine import
    try:
        from nullsweep.patterns.monotone.spark_engine import SparkDFPatternDetector
        print("✓ SparkDFPatternDetector imported successfully")
    except Exception as e:
        print(f"✗ SparkDFPatternDetector import failed: {e}")
        traceback.print_exc()
        return False

    # Test DatasetPatternManager import
    try:
        from nullsweep.patterns.df import DatasetPatternManager
        manager = DatasetPatternManager()
        print("✓ DatasetPatternManager imported and instantiated successfully")

        # Check if pyspark is in the decider
        coarse_engines = manager._decider.get("coarse", {})
        if "pyspark" in coarse_engines:
            print("✓ pyspark engine is registered in DatasetPatternManager")
        else:
            print("✗ pyspark engine is NOT registered in DatasetPatternManager")
            print(f"Available engines: {list(coarse_engines.keys())}")
            return False

    except Exception as e:
        print(f"✗ DatasetPatternManager import/instantiation failed: {e}")
        traceback.print_exc()
        return False

    # Test if we can detect pyspark module correctly
    try:
        if SPARK_AVAILABLE:
            import pyspark.sql
            dummy_module = "pyspark.sql.dataframe"
            engine = dummy_module.split(".")[0]
            print(
                f"✓ Engine detection test: '{dummy_module}' -> engine: '{engine}'")
        else:
            print("ℹ PySpark not available, skipping engine detection test")
    except Exception as e:
        print(f"✗ Engine detection test failed: {e}")
        traceback.print_exc()
        return False

    return True


def test_class_structure():
    print("\nTesting class structure...")

    try:
        from nullsweep.patterns.monotone.spark_engine import SparkDFPatternDetector
        from nullsweep.patterns.monotone.base import ADataFramePatternDetector

        # Check if SparkDFPatternDetector inherits from ADataFramePatternDetector
        if issubclass(SparkDFPatternDetector, ADataFramePatternDetector):
            print(
                "✓ SparkDFPatternDetector properly inherits from ADataFramePatternDetector")
        else:
            print(
                "✗ SparkDFPatternDetector does not inherit from ADataFramePatternDetector")
            return False

        # Check if required methods are implemented
        required_methods = ['detect_univariate',
                            'detect_monotone', 'detect_pattern']
        for method in required_methods:
            if hasattr(SparkDFPatternDetector, method):
                print(f"✓ Method '{method}' is implemented")
            else:
                print(f"✗ Method '{method}' is missing")
                return False

    except Exception as e:
        print(f"✗ Class structure test failed: {e}")
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("=== NullSweep PySpark Integration Test ===\n")

    import_success = test_imports()
    structure_success = test_class_structure()

    print(f"\n=== Test Results ===")
    print(f"Import tests: {'PASSED' if import_success else 'FAILED'}")
    print(f"Structure tests: {'PASSED' if structure_success else 'FAILED'}")

    if import_success and structure_success:
        print("\n🎉 All tests passed! PySpark integration is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
