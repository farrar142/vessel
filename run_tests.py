"""
Test runner script
테스트를 실행하는 간단한 스크립트
"""

import subprocess
import sys


def run_tests():
    """모든 테스트 실행"""
    print("=" * 70)
    print("PyDI Framework - 테스트 실행")
    print("=" * 70)

    # pytest 실행
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--tb=short",
        "--color=yes",
    ]

    result = subprocess.run(cmd)
    return result.returncode


def run_tests_with_coverage():
    """커버리지 포함 테스트 실행"""
    print("=" * 70)
    print("PyDI Framework - 커버리지 포함 테스트 실행")
    print("=" * 70)

    # pytest with coverage
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/",
        "-v",
        "--cov=pydi",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--color=yes",
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("✅ 모든 테스트 통과!")
        print("📊 커버리지 리포트: htmlcov/index.html")
        print("=" * 70)

    return result.returncode


if __name__ == "__main__":
    if "--coverage" in sys.argv or "-c" in sys.argv:
        sys.exit(run_tests_with_coverage())
    else:
        sys.exit(run_tests())
