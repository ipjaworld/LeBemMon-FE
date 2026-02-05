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
  /** 속성 약점/반감 배열 (예: ["불속성약점", "얼음속성약점"], null 가능) */
  attributes?: string[] | null;
  /** 드롭하는 아이템 ID 배열 */
  dropItemIds?: string[];
  /** 주요 드랍 아이템 ID 배열 (1~3개, null 가능) - 카드에 표시될 중요한 득템 */
  featuredDropItemIds?: string[] | null;
  /** 능력치 정보 (선택적) */
  stats?: {
    /** MP (마나 포인트) */
    mp?: number;
    /** 넉백 가능 데미지 (예: "0+" 형식의 문자열 또는 숫자) */
    knockbackDamage?: number | string;
    /** 물리 데미지 */
    physicalDamage?: number;
    /** 마법 데미지 */
    magicDamage?: number;
    /** 물리 방어력 */
    physicalDefense?: number;
    /** 마법 방어력 */
    magicDefense?: number;
    /** 속도 */
    speed?: number;
    /** 필요 명중 (해당 레벨에서의 필요 명중치) */
    requiredAccuracy?: number;
    /** 메소 (드롭 메소량) */
    mesos?: number;
  };
  /** 변신 전 몬스터 ID (이 몬스터가 다른 몬스터를 사냥하여 변신한 경우) */
  transformsFromMonsterId?: string;
}

