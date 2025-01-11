# import json


# USERMENU = """
#     ++++++++++++++++++++++++++++++
#     a - Thêm sách
#     l - Hiển thị tát cả cuốn sách
#     d - Xóa cuốn sách theo id
#     f - Tìm kiếm cuốn sách theo id
#     q - Thoat
#     ++++++++++++++++++++++++++++++
#     Lựa chọn của bạn: 
#  """    
 
# opearations = {
#     'a': add_book,
#     'l': list_all,
#     'd': delete_book,
#     'f': find_book,
#     'q': exit_
# }

     
 
# class Book:
#     def __init__(self, title, author, year):
#         self.title = title
#         self.author = author
#         self.year = year
        
# class BookManager:
#     def __init__(self,):
#         self.books = []
#     def add_book(self, title, author,year):
#         book = Book(title, author, year)
#         self.books.append(book)
#         print('Thêm sách thành công')
#     def list_all(self):
#         if not self.books:
#             print('Danh sách trống')
#         else:
#             for index, book in enumerate(self.books, start=1):
#                 print(f""" Thông tin cuốn sách No {index}:
#                       Title: {book.title}
#                       Author: {book.author}
#                       Year: {book.year}
#                       """)
#     def delete_book(self, title):
#         if self.books:
#             found = [_book for _book in self.books if _book.title == title]
#             if found:
#                 self.books.remove(found[0])
#                 print(f'Xóa thành công cuốn sách {title}')
#             else:
#                 print('Tên cuốn sách không tồn tại!')
#         else:
#             print('Danh sách rỗng!')
#     def update_book(self, title, new_author,new_year):
#         if self.books:
#             found = [index for index,_book in enumerate(self.books) if _book.title == title]
#             if found:
#                 self.books[found[0]].author = new_author
#                 self.books[found[0]].year = new_year 
#                 print(f'Cập nhật thành công cuốn sách {title}')
#             else:
#                 print('Tên cuốn  cập nhậtnhật không tồn tại!')
#         else:
#             print('Danh sách rỗng!')

# class app:
#     def __init__(self, app_menu, operations):
#         self.app_menu = app_menu
#         self.operations = operations
#     def menu(self):
#         choose = input(self.app_menu)
#         while choose != 'q':
#             if choose not in list(self.operations.keys):
#                 print('Lựa chọn không hợp lệ. Đề nghị nhập lại!')
#                 choose = input(self.app_menu)
#             else:
#                 switch(choose):
#                     case 
    
import sqlite3

Path = r'D:\My Project\Agent_Hunting\data.db'                                                               

with sqlite3.connect(Path) as conn:
    cursor = conn.cursor()
    
    # Sửa câu lệnh UPDATE
    cursor.execute("""
        UPDATE Config
        SET Filter = '1'
    """)

    # Commit thay đổi vào cơ sở dữ liệu
    conn.commit()

    # Kiểm tra kết quả cập nhật
    cursor.execute("SELECT * FROM Config WHERE Object = 'File' AND Action = 'Create'")
    rows = cursor.fetchall()

    # Hiển thị dữ liệu
    print(f"\nDữ liệu trong bảng Config sau khi cập nhật:")
    for row in rows:
        print(row)
 