/**
 * 한글 초성 추출 및 검색 유틸리티
 */

// 한글 초성 배열
const 초성배열 = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'];

/**
 * 한글 문자의 초성을 추출합니다
 */
export function get초성(char: string): string {
  const code = char.charCodeAt(0);
  // 한글 유니코드 범위: 0xAC00 ~ 0xD7A3
  if (code >= 0xac00 && code <= 0xd7a3) {
    const 초성인덱스 = Math.floor((code - 0xac00) / 28 / 21);
    return 초성배열[초성인덱스];
  }
  return '';
}

/**
 * 문자열의 모든 초성을 추출합니다
 */
export function get초성문자열(text: string): string {
  return text
    .split('')
    .map((char) => get초성(char) || char)
    .join('');
}

/**
 * 입력 텍스트가 검색어와 매칭되는지 확인합니다
 * - 완전 일치
 * - 초성 일치
 * - 부분 문자열 일치
 */
export function matchesSearch(text: string, searchQuery: string): boolean {
  if (!searchQuery.trim()) return true;
  
  const lowerText = text.toLowerCase();
  const lowerQuery = searchQuery.toLowerCase();
  
  // 완전 일치 또는 부분 문자열 일치
  if (lowerText.includes(lowerQuery)) return true;
  
  // 초성 검색
  const text초성 = get초성문자열(text);
  const query초성 = get초성문자열(searchQuery);
  
  if (text초성.includes(query초성)) return true;
  
  return false;
}

/**
 * 검색어와의 매칭 점수를 계산합니다 (정렬용)
 * 점수가 높을수록 더 우선순위가 높습니다
 */
export function getMatchScore(text: string, searchQuery: string): number {
  if (!searchQuery.trim()) return 0;
  
  const lowerText = text.toLowerCase();
  const lowerQuery = searchQuery.toLowerCase();
  
  // 완전 일치 (가장 높은 점수)
  if (lowerText === lowerQuery) return 1000;
  
  // 시작 부분 일치
  if (lowerText.startsWith(lowerQuery)) return 800;
  
  // 부분 문자열 일치
  if (lowerText.includes(lowerQuery)) return 600;
  
  // 초성 완전 일치
  const text초성 = get초성문자열(text);
  const query초성 = get초성문자열(searchQuery);
  
  if (text초성 === query초성) return 500;
  
  // 초성 시작 부분 일치
  if (text초성.startsWith(query초성)) return 400;
  
  // 초성 부분 일치
  if (text초성.includes(query초성)) return 200;
  
  return 0;
}
