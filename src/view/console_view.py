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
