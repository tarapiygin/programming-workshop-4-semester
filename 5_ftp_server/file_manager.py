import os
import shutil
import zipfile


class FileManager:

    def __init__(self, current_path, working_directory):
        self.current_path = current_path
        self.working_directory = working_directory

    def create_folder(self, folder_name):
        os.makedirs(os.path.join(self.current_path, folder_name), exist_ok=True)

    def delete_folder(self, folder_name):
        shutil.rmtree(os.path.join(self.current_path, folder_name))

    def change_directory(self, folder_name):
        new_path = os.path.join(self.current_path, folder_name)
        if not new_path.startswith(self.working_directory):
            print("Извините, операция запрещена")
        else:
            self.current_path = new_path

    def create_file(self, file_name):
        open(os.path.join(self.current_path, file_name), 'a').close()

    def delete_file(self, file_name):
        os.remove(os.path.join(self.current_path, file_name))

    def write_to_file(self, file_name, content):
        with open(os.path.join(self.current_path, file_name), 'w') as f:
            f.write(content)

    def read_file(self, file_name):
        with open(os.path.join(self.current_path, file_name), 'r') as f:
            print(f.read())

    def copy_file(self, file_name, new_folder):
        shutil.copy(os.path.join(self.current_path, file_name),
                    os.path.join(self.working_directory, new_folder))

    def move_file(self, file_name, new_folder):
        shutil.move(os.path.join(self.current_path, file_name),
                    os.path.join(self.working_directory, new_folder))

    def rename_file(self, old_file_name, new_file_name):
        os.rename(
            os.path.join(self.current_path, old_file_name),
            os.path.join(self.current_path, new_file_name)
        )

    def move_up(self):
        new_path = os.path.dirname(self.current_path)
        if not new_path.startswith(self.working_directory):
            print("Изивните, операция запрещена")
        else:
            self.current_path = new_path

    def print_current_path(self):
        print("Текущий путь:", self.current_path)

    def archive(self, target_name, archive_name):
        """Архивация файла или папки. Функции архивации и разархивации работают только с zip-файлами.
        Для работы с другими форматами архивов можно использовать py7zr"""
        archive_path = os.path.join(self.current_path, archive_name)
        target_path = os.path.join(self.current_path, target_name)
        if os.path.isfile(target_path):
            with zipfile.ZipFile(archive_path, 'w') as zipf:
                zipf.write(target_path, arcname=os.path.basename(target_path))
        elif os.path.isdir(target_path):
            with zipfile.ZipFile(archive_path, 'w') as zipf:
                for foldername, subfolders, filenames in os.walk(target_path):
                    for filename in filenames:
                        # создать полный путь файла
                        file_path = os.path.join(foldername, filename)
                        # добавить файл в zip-файл
                        zipf.write(file_path, arcname=os.path.relpath(file_path, start=self.current_path))
        else:
            print(f"Путь '{target_path}' не существует")

    def unarchive(self, archive_name, extract_folder=None):
        """Разархивация файла"""
        archive_path = os.path.join(self.current_path, archive_name)
        extract_path = self.current_path if extract_folder is None else os.path.join(self.current_path, extract_folder)
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(path=extract_path)
