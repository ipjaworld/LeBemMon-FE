import re
import json
from pathlib import Path

def parse_monster_data(file_path):
    """
    HTML 파일에서 몬스터 정보를 추출하여 JSON으로 변환
    """
    print(f"파일 읽는 중: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 각 몬스터 블록을 찾기 위한 패턴
    # <a class="search-page-add-content-box" ...> 부터 </a> 까지
    monster_pattern = r'<a class="search-page-add-content-box"[^>]*>(.*?)</a>'
    
    monsters = []
    matches = re.finditer(monster_pattern, content, re.DOTALL)
    
    for idx, match in enumerate(matches, 1):
        block = match.group(1)
        
        try:
            # 몬스터 ID (name 속성)
            id_match = re.search(r'name="(\d+)"', block)
            monster_id = id_match.group(1) if id_match else None
            
            # 이미지 URL (src 속성)
            img_match = re.search(r'src="([^"]+)"', block)
            image_url = img_match.group(1) if img_match else None
            
            # 몬스터 이름 (h3 태그 내용)
            name_match = re.search(r'<h3[^>]*>(.*?)</h3>', block)
            name = name_match.group(1).strip() if name_match else None
            
            # LEVEL, HP, EXP 추출
            # favorite-item-info-text 클래스의 div들을 찾음
            info_texts = re.findall(r'<span class="favorite-item-info-text">.*?<div>([^<]+)</div>.*?<div>([^<]+)</div>', block, re.DOTALL)
            
            level = None
            hp = None
            exp = None
            
            # info_texts는 [(라벨, 값), ...] 형태
            for label, value in info_texts:
                label = label.strip()
                value = value.strip().replace(',', '')  # 쉼표 제거 (예: 18,000 -> 18000)
                
                if label == 'LEVEL':
                    level = int(value) if value.isdigit() else None
                elif label == 'HP':
                    hp = int(value) if value.isdigit() else None
                elif label == 'EXP':
                    exp = int(value) if value.isdigit() else None
            
            monster_data = {
                'id': monster_id,
                'name': name,
                'imageUrl': image_url,
                'level': level,
                'hp': hp,
                'exp': exp
            }
            
            monsters.append(monster_data)
            
            if idx % 100 == 0:
                print(f"처리 중: {idx}개 몬스터 추출 완료...")
                
        except Exception as e:
            print(f"오류 발생 (몬스터 #{idx}): {e}")
            continue
    
    return monsters

def main():
    # 입력 파일 경로
    input_file = r"c:\Users\tbrk7\OneDrive\문서\메랜 몬스터 db.txt"
    
    # 출력 파일 경로 (프로젝트 루트에 저장)
    output_file = Path(__file__).parent / "monster_data.json"
    
    print("몬스터 데이터 파싱 시작...")
    monsters = parse_monster_data(input_file)
    
    print(f"\n총 {len(monsters)}개의 몬스터 데이터 추출 완료!")
    
    # JSON 파일로 저장
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(monsters, f, ensure_ascii=False, indent=2)
    
    print(f"데이터가 {output_file}에 저장되었습니다.")
    
    # 샘플 데이터 출력 (처음 3개)
    if monsters:
        print("\n=== 샘플 데이터 (처음 3개) ===")
        for monster in monsters[:3]:
            print(json.dumps(monster, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
