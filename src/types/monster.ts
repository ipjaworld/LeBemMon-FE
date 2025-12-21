export interface Monster {
  id: string;
  name: string;
  imageUrl: string;
  level: number;
  hp: number;
  exp: number;
  isReleased: boolean;
  /** 출몰 지역/마을 ID 배열 (지역 데이터 마이그레이션 전까지는 선택적 필드) */
  regionIds?: string[];
}

