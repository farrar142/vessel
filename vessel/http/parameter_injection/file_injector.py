"""
File upload parameter injector
"""

from typing import Any, Optional, Tuple, get_origin, get_args, Union, Annotated
import inspect

from vessel.http.parameter_injection.base import ParameterInjector, InjectionContext
from vessel.http.file_upload import (
    UploadedFile,
    parse_file_from_dict,
    parse_files_from_list,
)
from vessel.validation import ValidationError


class FileInjector(ParameterInjector):
    """파일 업로드 파라미터 주입 (Annotated 구문 지원)"""

    def can_inject(self, context: InjectionContext) -> bool:
        """UploadedFile 타입 또는 Annotated[UploadedFile, "key"] 타입인 경우"""
        param_type = context.param_type
        origin = get_origin(param_type)

        # Annotated[UploadedFile, "key"] 체크
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == UploadedFile:
                return True

        # UploadedFile 직접 체크
        if param_type == UploadedFile:
            return True

        # Optional[UploadedFile] 또는 Optional[Annotated[UploadedFile, "key"]] 체크
        if origin is Union:
            args = get_args(param_type)
            for arg in args:
                if arg == UploadedFile:
                    return True
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == UploadedFile:
                        return True

        # list[UploadedFile] 또는 list[Annotated[UploadedFile, "key"]] 체크
        if origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                if list_item_type == UploadedFile:
                    return True
                # list[Annotated[UploadedFile, "key"]] 체크
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if list_item_args and list_item_args[0] == UploadedFile:
                        return True

        return False

    def inject(self, context: InjectionContext) -> Tuple[Optional[Any], bool]:
        """파일 값을 주입 (Annotated로 명시된 키 또는 파라미터 이름 사용)"""
        param_type = context.param_type
        param_name = context.param_name
        request_data = context.request_data

        origin = get_origin(param_type)

        # 명시적 키 추출 (Annotated에서)
        explicit_key = self._extract_explicit_key(param_type)
        
        # Optional 여부 확인
        is_optional = self._is_optional(param_type)
        
        # 리스트 여부 확인
        is_list = self._is_list(param_type)

        # 파일 키 결정
        file_key = explicit_key if explicit_key else param_name

        # 파일 데이터 가져오기
        file_data = request_data.get(file_key)
        
        if file_data is None:
            if is_optional:
                return None, False
            # 필수 파라미터인 경우 에러
            raise ValidationError(
                [
                    {
                        "field": param_name,
                        "message": f"Required file '{file_key}' is missing",
                    }
                ]
            )

        # 파일 데이터인지 확인
        if not self._is_file_data(file_data):
            # 파일 데이터가 아니면 건너뜀
            return None, False

        # list[UploadedFile] 처리
        if is_list:
            return self._inject_file_list(file_key, file_data)

        # 단일 파일 처리
        return self._inject_single_file(file_key, file_data, is_optional)

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

    def _extract_explicit_key(self, param_type: Any) -> Optional[str]:
        """Annotated 타입에서 명시적으로 지정된 파일 키 추출"""
        origin = get_origin(param_type)

        # Annotated[UploadedFile, "key"]에서 추출
        if origin is Annotated:
            args = get_args(param_type)
            if args and args[0] == UploadedFile and len(args) > 1:
                return args[1]

        # Optional[Annotated[UploadedFile, "key"]]에서 추출
        if origin is Union:
            for arg in get_args(param_type):
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == UploadedFile and len(arg_args) > 1:
                        return arg_args[1]

        # list[Annotated[UploadedFile, "key"]]에서 추출
        if origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if (
                        list_item_args
                        and list_item_args[0] == UploadedFile
                        and len(list_item_args) > 1
                    ):
                        return list_item_args[1]

        return None

    def _is_optional(self, param_type: Any) -> bool:
        """Optional 타입인지 확인"""
        origin = get_origin(param_type)
        if origin is Union:
            args = get_args(param_type)
            has_none = type(None) in args
            has_uploaded_file = False

            for arg in args:
                if arg == UploadedFile:
                    has_uploaded_file = True
                    break
                arg_origin = get_origin(arg)
                if arg_origin is Annotated:
                    arg_args = get_args(arg)
                    if arg_args and arg_args[0] == UploadedFile:
                        has_uploaded_file = True
                        break

            return has_none and has_uploaded_file

        return False

    def _is_list(self, param_type: Any) -> bool:
        """list[UploadedFile] 타입인지 확인"""
        origin = get_origin(param_type)
        if origin is list:
            args = get_args(param_type)
            if args:
                list_item_type = args[0]
                # list[UploadedFile]
                if list_item_type == UploadedFile:
                    return True
                # list[Annotated[UploadedFile, "key"]]
                list_item_origin = get_origin(list_item_type)
                if list_item_origin is Annotated:
                    list_item_args = get_args(list_item_type)
                    if list_item_args and list_item_args[0] == UploadedFile:
                        return True
        return False

    @property
    def priority(self) -> int:
        """파일 처리 우선순위"""
        return 200
