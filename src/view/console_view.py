class ConsoleView:
    def render_main_menu(self, summary):
        lines = [
            "=== 반도체 시료 생산주문관리 시스템 ===",
            f"등록 시료 수: {summary['sample_count']}개 | 총 재고: {summary['total_stock']}개",
            "1. 시료 관리",
            "2. 주문 (접수 / 승인 / 거절)",
            "3. 모니터링",
            "4. 출고 처리",
            "5. 생산 라인",
        ]
        return "\n".join(lines)

    def render_sample_menu(self):
        lines = [
            "--- 시료 관리 ---",
            "1. 등록",
            "2. 조회",
            "3. 검색",
            "0. 뒤로가기",
        ]
        return "\n".join(lines)

    def render_order_menu(self):
        lines = [
            "--- 주문 ---",
            "1. 예약",
            "2. 접수된 목록 조회",
            "3. 승인",
            "4. 거절",
            "0. 뒤로가기",
        ]
        return "\n".join(lines)

    def render_sample_list(self, samples):
        if not samples:
            return "등록된 시료가 없습니다."
        lines = [
            f"[{sample['sample_id']}] {sample['name']} (재고: {sample['stock']})"
            for sample in samples
        ]
        return "\n".join(lines)
