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

    def render_monitoring_menu(self):
        lines = [
            "--- 모니터링 ---",
            "1. 주문량 조회",
            "2. 재고량 조회",
            "0. 뒤로가기",
        ]
        return "\n".join(lines)

    def render_order_counts(self, counts):
        return "\n".join(f"{status}: {count}" for status, count in counts.items())

    def render_release_menu(self):
        lines = [
            "--- 출고 처리 ---",
            "1. 목록 조회",
            "2. 출고 실행",
            "0. 뒤로가기",
        ]
        return "\n".join(lines)

    def render_production_menu(self):
        lines = [
            "--- 생산 라인 ---",
            "1. 생산 현황 조회",
            "2. 대기 큐 조회",
            "3. 생산 완료 처리",
            "0. 뒤로가기",
        ]
        return "\n".join(lines)

    def render_stock_statuses(self, statuses):
        if not statuses:
            return "등록된 시료가 없습니다."
        lines = [
            f"[{status['sample_id']}] 재고: {status['stock']} ({status['status']})"
            for status in statuses
        ]
        return "\n".join(lines)

    def render_order_list(self, orders):
        if not orders:
            return "주문이 없습니다."
        lines = [
            f"[{order['order_id']}] {order['customer_name']} - {order['sample_id']} x{order['quantity']} ({order['status']})"
            for order in orders
        ]
        return "\n".join(lines)
