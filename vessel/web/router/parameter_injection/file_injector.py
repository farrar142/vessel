"""
File upload parameter injector
"""

from typing import Any, Optional

from vessel.web.router.parameter_injection.annotated_value_injector import (
    AnnotatedValueInjector,
)
from vessel.web.router.parameter_injection.base import InjectionContext
from vessel.web.http.uploaded_file import (
    UploadedFile,
    parse_file_from_dict,
    parse_files_from_list,
)


class FileInjector(AnnotatedValueInjector):
    """파일 업로드 파라미터 주입 (Annotated 구문 지원, 리스트 지원)"""

    def get_marker_type(self) -> type:
        """UploadedFile 타입 반환"""
        return UploadedFile

    def supports_list(self) -> bool:
        """list[UploadedFile] 지원"""
        return True

    def extract_value_from_request(
        self, context: InjectionContext, name: str
    ) -> Optional[Any]:
        """요청에서 파일 데이터 추출"""
        file_data = context.request_data.get(name)

        # 파일 데이터인지 확인
        if file_data is not None and not self._is_file_data(file_data):
            # 파일 데이터가 아니면 None 반환
            return None

        return file_data

    def get_default_name(self, param_name: str) -> str:
        """파라미터 이름을 파일 키로 변환 (변환 없이 그대로 사용)"""
        return param_name

    def create_value_object(self, name: str, value: Any) -> Optional[UploadedFile]:
        """UploadedFile 값 객체 생성"""
        # 리스트로 전달된 경우 첫 번째 항목 사용
        if isinstance(value, list):
            if len(value) == 0:
                return None
            value = value[0]

        # 파일 데이터 파싱
        uploaded_file = parse_file_from_dict(value)
        return uploaded_file

    def create_value_list(self, name: str, values: list) -> list[UploadedFile]:
        """UploadedFile 리스트 생성"""
        # 단일 파일을 리스트로 변환
        if not isinstance(values, list):
            values = [values]

        # 파일 리스트 파싱
        uploaded_files = parse_files_from_list(values)
        return uploaded_files

    def get_error_message(self, name: str, param_name: str) -> str:
        """필수 파일 누락 에러 메시지"""
        return f"Required file '{name}' is missing"

    def _is_file_data(self, value: Any) -> bool:
        """파일 데이터인지 확인"""
        # 딕셔너리이고 filename과 content 키가 있으면 파일 데이터
        if isinstance(value, dict) and "filename" in value and "content" in value:
            return True
        # 리스트이고 각 항목이 파일 데이터면 파일 리스트
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return "filename" in value[0]
        return False

    @property
    def priority(self) -> int:
        """파일 처리 우선순위"""
        return 200
