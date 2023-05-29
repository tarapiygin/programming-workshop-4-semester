from file_manager import FileManager
from settings import WORKING_DIRECTORY


def main():
    fm = FileManager(WORKING_DIRECTORY, WORKING_DIRECTORY)
    while True:
        print('1 - Создать папку')
        print('2 - Удалить папку')
        print('3 - Перейти в папку')
        print('4 - Перейти на уровень вверх')
        print('5 - Создать файл')
        print('6 - Удалить файл')
        print('7 - Записать в файл')
        print('8 - Прочитать файл')
        print('9 - Копировать файл')
        print('10 - Переместить файл')
        print('11 - Переименовать файл')
        print('12 - Архивировать файл/папку')
        print('13 - Разархивировать файл')
        print('0 - Выйти')
        fm.print_current_path()
        choice = input('Введите номер команды: ')
        if choice == '1':
            name = input('Введите имя папки: ')
            fm.create_folder(name)
        elif choice == '2':
            name = input('Введите имя папки: ')
            fm.delete_folder(name)
        elif choice == '3':
            name = input('Введите имя папки: ')
            fm.change_directory(name)
        elif choice == '4':
            fm.move_up()
        elif choice == '5':
            name = input('Введите имя файла: ')
            fm.create_file(name)
        elif choice == '6':
            name = input('Введите имя файла: ')
            fm.delete_file(name)
        elif choice == '7':
            name = input('Введите имя файла: ')
            content = input('Введите текст: ')
            fm.write_to_file(name, content)
        elif choice == '8':
            name = input('Введите имя файла: ')
            fm.read_file(name)
        elif choice == '9':
            name = input('Введите имя файла: ')
            folder = input('Введите папку назначения: ')
            fm.copy_file(name, folder)
        elif choice == '10':
            name = input('Введите имя файла: ')
            folder = input('Введите папку назначения: ')
            fm.move_file(name, folder)
        elif choice == '11':
            old_name = input('Введите старое имя файла: ')
            new_name = input('Введите новое имя файла: ')
            fm.rename_file(old_name, new_name)
        elif choice == '12':
            name = input('Введите имя файла/папки для архивации: ')
            archive_name = input('Введите имя архива: ')
            fm.archive(name, archive_name)
        elif choice == '13':
            name = input('Введите имя архива для разархивации: ')
            extract_folder = input('Введите имя папки для извлечения (можно оставить пустым): ')
            fm.unarchive(name, extract_folder)
        elif choice == '0':
            break


if __name__ == "__main__":
    main()
