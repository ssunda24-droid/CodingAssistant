
from app.tools.filesystem import (
    read_file,
    write_file,
    list_files,
    search_in_files,
    edit_file
)



def main():
    path = "edit_test.txt"

    # 1. Create the test file first.
    write_file(path, "Hello world!")
    print("Created test file.")

    # 2. Confirm the file exists and has content.
    print("\n--- BEFORE EDIT ---")
    print(read_file(path))

    # 3. Edit the file.
    edit_file(
        path=path,
        old_text="world",
        new_text="CodingAssistant",
    )

    # 4. Verify the updated content.
    print("\n--- AFTER EDIT ---")
    print(read_file(path))

    # 5. Delete the temporary test file.
    from app.tools.filesystem import _get_safe_path
    _get_safe_path(path).unlink()


if __name__ == "__main__":
    main()