from storage import load_data, save_data


def create_item():
    data = load_data()
    new_id = max((item["id"] for item in data), default=0) + 1

    name = input("이름: ").strip()
    email = input("이메일: ").strip()

    data.append({"id": new_id, "name": name, "email": email})
    save_data(data)
    print(f"[생성 완료] id={new_id}")


def read_all():
    data = load_data()
    if not data:
        print("데이터가 없습니다.")
        return
    for item in data:
        print(item)


def read_one():
    data = load_data()
    target_id = input("조회할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            print(item)
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")


def update_item():
    data = load_data()
    target_id = input("수정할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            new_name = input(f"이름 ({item['name']}, 그대로면 Enter): ").strip()
            new_email = input(f"이메일 ({item['email']}, 그대로면 Enter): ").strip()

            if new_name:
                item["name"] = new_name
            if new_email:
                item["email"] = new_email

            save_data(data)
            print(f"[수정 완료] id={target_id}")
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")


def delete_item():
    data = load_data()
    target_id = input("삭제할 id: ").strip()

    for item in data:
        if str(item["id"]) == target_id:
            confirm = input(f"'{item}' 항목을 삭제하시겠습니까? (y/n): ").strip().lower()
            if confirm == "y":
                data.remove(item)
                save_data(data)
                print(f"[삭제 완료] id={target_id}")
            else:
                print("삭제가 취소되었습니다.")
            return

    print(f"id={target_id} 데이터를 찾을 수 없습니다.")
