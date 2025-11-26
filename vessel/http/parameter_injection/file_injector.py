"""
File upload parameter injector
"""

from typing import Any, Optional, Tuple, get_origin, get_args, Union
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.file_upload import (
    UploadedFile,
    parse_file_from_dict,
    parse_files_from_list,
)
from vessel.validation import ValidationError


class FileInjector(ParameterInjector):
    """파일 업로드 파라미터 주입"""

    def can_inject(self, context: InjectionContext) -> bool:
        """UploadedFile 타입인 경우"""
        param_type = context.param_type
        origin = get_origin(param_type)

        # UploadedFile 직접 체크
        if param_type == UploadedFile:
            return True

        # Optional[UploadedFile] 체크
        if origin is Union:
            args = get_args(param_type)
            if UploadedFile in args and type(None) in args:
                return True

        # list[UploadedFile] 체크
        if origin is list:
            args = get_args(param_type)
            if args and args[0] == UploadedFile:
                return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """파일 값을 주입"""
        param_type = context.param_type
        param_name = context.param_name
        request_data = context.request_data

        origin = get_origin(param_type)

        # 파일 데이터가 없으면 건너뜀
        file_data = request_data.get(param_name)
        if file_data is None:
            # Optional인 경우 None 반환
            if origin is Union:
                args = get_args(param_type)
                if UploadedFile in args and type(None) in args:
                    return None, False
            # 필수 파라미터인 경우 에러
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"Required file '{param_name}' is missing",
                    }
                ]
            )

        # 파일 데이터인지 확인
        if not self._is_file_data(file_data):
            # 파일 데이터가 아니면 건너뜀
            return None, False

        # list[UploadedFile] 처리
        if origin is list:
            args = get_args(param_type)
            if args and args[0] == UploadedFile:
                return self._inject_file_list(param_name, file_data)

        # Optional[UploadedFile] 처리
        is_optional = False
        if origin is Union:
            args = get_args(param_type)
            if UploadedFile in args and type(None) in args:
                is_optional = True

        # 단일 파일 또는 Optional 파일 처리
        return self._inject_single_file(param_name, file_data, is_optional)

    def _is_file_data(self, value: Any) -> bool:
        """파일 데이터인지 확인"""
        # 딕셔너리이고 filename과 content 키가 있으면 파일 데이터
        if isinstance(value, dict) and "filename" in value and "content" in value:
            return True
        # 리스트이고 각 항목이 파일 데이터면 파일 리스트
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return "filename" in value[0]
        return False

    def _inject_single_file(
        self, param_name: str, file_data: Any, is_optional: bool
    ) -> Tuple[Optional[Any], bool]:
        """단일 파일 주입"""
        # 리스트로 전달된 경우 첫 번째 항목 사용
        if isinstance(file_data, list):
            if len(file_data) == 0:
                if is_optional:
                    return None, True
                else:
                    raise ValidationError(
                        [
                            {
                                "field": param_name,
                                "message": f"Required file '{param_name}' is missing",
                            }
                        ]
                    )
            file_data = file_data[0]

        # 파일 데이터 파싱
        uploaded_file = parse_file_from_dict(file_data)
        return uploaded_file, True

    def _inject_file_list(self, param_name: str, file_data: Any) -> Tuple[Any, bool]:
        """파일 리스트 주입"""
        # 단일 파일을 리스트로 변환
        if not isinstance(file_data, list):
            file_data = [file_data]

        # 파일 리스트 파싱
        uploaded_files = parse_files_from_list(file_data)
        return uploaded_files, True

    @property
    def priority(self) -> int:
        """파일 처리 우선순위"""
        return 200
