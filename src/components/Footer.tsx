export default function Footer() {
  return (
    <footer className="mt-16 border-t border-gray-800 bg-gray-900 py-8">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 text-center sm:flex-row sm:text-left">
          <div className="flex flex-col gap-1">
            <p className="text-sm text-gray-400">
              메이플랜드 레범몬
            </p>
            <p className="text-xs text-gray-500">
              메이플스토리월드 메이플랜드 레벨 범위 몬스터 검색 서비스
            </p>
          </div>
          <div className="flex flex-col gap-1">
            <p className="text-xs text-gray-500">
              오류 제보 및 제안은
            </p>
            <a
              href="mailto:ipjaworld@gmail.com"
              className="text-sm text-gray-400 hover:text-blue-400 transition-colors"
            >
              ipjaworld@gmail.com
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}

