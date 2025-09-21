import file_utils as fu

# Test: Create a sample file
with open("test.txt", "w") as f:
    f.write("Hello, world!")

# Copy file
fu.copy_file("test.txt", "copy_test.txt", overwrite=True)

# Move file
fu.move_file("copy_test.txt", "moved_test.txt", overwrite=True)

# Rename file
fu.rename_file("moved_test.txt", "renamed_test.txt")

# List files
print("Files in current directory:", fu.list_files("."))

# Delete file
fu.delete_file("renamed_test.txt")
