/**
 * 직업 타입 정의
 */

/** 직업 대분류 ID */
export type JobCategoryId = 
  | 'common'    // 공통 (전직업)
  | 'warrior'   // 전사
  | 'mage'      // 마법사
  | 'archer'    // 궁수
  | 'rogue'     // 도적
  | 'pirate'    // 해적
  | 'evan'      // 에반
  | 'aran';     // 아란

/** 직업 세부 분류 ID */
export type JobSubCategoryId =
  // 전사
  | 'warrior-common'  // 전사 공통
  | 'hero'            // 히어로
  | 'dark-knight'     // 다크나이트
  | 'paladin'         // 팔라딘
  // 마법사
  | 'mage-common'     // 마법사 공통
  | 'bishop'          // 비숍
  | 'arch-mage-fp'    // 불.독 아크메이지
  | 'arch-mage-il'    // 썬.콜 아크메이지
  // 궁수
  | 'archer-common'   // 궁수 공통
  | 'bow-master'      // 보우마스터
  | 'marksman'        // 신궁
  // 도적
  | 'rogue-common'    // 도적 공통
  | 'night-lord'      // 나이트로드
  | 'shadower'        // 섀도어
  // 해적
  | 'pirate-common'   // 해적 공통
  | 'captain'         // 캡틴
  | 'viper';          // 바이퍼

/**
 * 직업 카테고리 인터페이스
 */
export interface JobCategory {
  /** 직업 카테고리 ID */
  id: JobCategoryId;
  
  /** 직업 카테고리 이름 */
  name: string;
  
  /** 출시 여부 */
  isReleased: boolean;
  
  /** 직업 세부 분류 목록 */
  subCategories?: JobSubCategory[];
}

/**
 * 직업 세부 분류 인터페이스
 */
export interface JobSubCategory {
  /** 세부 분류 ID */
  id: JobSubCategoryId;
  
  /** 세부 분류 이름 */
  name: string;
  
  /** 부모 카테고리 ID */
  parentId: JobCategoryId;
}

