"""
스크립트 공통 유틸리티
"""
from pathlib import Path

# 프로젝트 루트 디렉토리 (scripts/ 폴더의 부모 디렉토리)
PROJECT_ROOT = Path(__file__).parent.parent


def get_data_path(filename: str) -> Path:
    """
    src/data/ 폴더 내 파일의 경로를 반환합니다.
    
    Args:
        filename: 파일 이름 (예: 'monster_data.json')
    
    Returns:
        파일의 전체 경로
    """
    return PROJECT_ROOT / "src" / "data" / filename


def get_root_path(filename: str) -> Path:
    """
    프로젝트 루트 디렉토리 내 파일의 경로를 반환합니다.
    
    Args:
        filename: 파일 이름
    
    Returns:
        파일의 전체 경로
    """
    return PROJECT_ROOT / filename

