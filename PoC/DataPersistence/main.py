from crud import create_item, read_all, read_one, update_item, delete_item


def print_menu():
    print("\n=== JSON CRUD ===")
    print("1. Create  2. Read All  3. Read One  4. Update  5. Delete  6. Exit")


def main():
    while True:
        print_menu()
        choice = input("선택: ").strip()

        if choice == "1":
            create_item()
        elif choice == "2":
            read_all()
        elif choice == "3":
            read_one()
        elif choice == "4":
            update_item()
        elif choice == "5":
            delete_item()
        elif choice == "6":
            print("종료합니다.")
            break
        else:
            print("잘못된 입력입니다.")


if __name__ == "__main__":
    main()
