import main
import storage


def test_full_crud_scenario_end_to_end(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(storage, "DATA_FILE", str(tmp_path / "data.json"))

    inputs = iter(
        [
            "2",  # 1. Read All (데이터 없음 확인)
            "1",
            "홍길동",
            "hong@example.com",  # 2. Create id=1
            "1",
            "김철수",
            "kim@example.com",  # 2. Create id=2
            "2",  # 3. Read All (2건 확인)
            "3",
            "1",  # 4. Read One id=1
            "4",
            "1",
            "",
            "new@example.com",  # 5. Update id=1 email만 변경
            "3",
            "1",  # 5. Read One으로 재확인
            "5",
            "2",
            "n",  # 6. Delete id=2 시도 → 취소
            "5",
            "2",
            "y",  # 6. Delete id=2 재시도 → 삭제
            "2",  # 7. Read All (id=1만 남음)
            "6",  # 종료
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))

    main.main()

    captured = capsys.readouterr()
    assert "데이터가 없습니다." in captured.out
    assert "[생성 완료] id=1" in captured.out
    assert "[생성 완료] id=2" in captured.out
    assert "[수정 완료] id=1" in captured.out
    assert "삭제가 취소되었습니다." in captured.out
    assert "[삭제 완료] id=2" in captured.out
    assert "종료합니다." in captured.out

    final_data = storage.load_data()
    assert final_data == [{"id": 1, "name": "홍길동", "email": "new@example.com"}]
