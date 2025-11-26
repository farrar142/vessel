"""
PackageScanner - 패키지 스캐닝 책임
"""

import importlib
import pkgutil
import sys
from typing import List


class PackageScanner:
    """패키지를 스캔하여 모듈들을 import하는 클래스"""

    @staticmethod
    def scan_packages(*packages: str) -> None:
        """
        지정된 패키지들을 스캔하여 모든 모듈을 import

        Args:
            *packages: 스캔할 패키지 이름들
        """
        for package_name in packages:
            PackageScanner._scan_package(package_name)

    @staticmethod
    def _scan_package(package_name: str) -> None:
        """
        단일 패키지를 스캔하여 모듈을 import

        Args:
            package_name: 스캔할 패키지 이름
        """
        try:
            # 패키지 또는 모듈 import
            if package_name in sys.modules:
                package = sys.modules[package_name]
            else:
                package = importlib.import_module(package_name)

            # 패키지인 경우 하위 모듈들도 재귀적으로 import
            if hasattr(package, "__path__"):
                package_path = package.__path__
                for importer, modname, ispkg in pkgutil.walk_packages(
                    path=package_path,
                    prefix=package.__name__ + ".",
                    onerror=lambda x: None,
                ):
                    try:
                        importlib.import_module(modname)
                    except Exception as e:
                        print(f"Warning: Failed to import {modname}: {e}")

        except Exception as e:
            print(f"Warning: Failed to scan package {package_name}: {e}")
