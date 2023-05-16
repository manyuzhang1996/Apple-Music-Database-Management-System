import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QHeaderView
from mydbutils import do_query, make_connection


class updateDialog(QDialog):
    """
    The update dialog.
    """

    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        # Load the dialog components.
        self.ui = uic.loadUi('update_dialog.ui')

        # 下拉框选table
        self.ui.table_comboBox.currentIndexChanged.connect(self._initialize_table)

        # search
        self.ui.search_pushButton.clicked.connect(self._search_data)

        # update
        self.ui.update_pushButton.clicked.connect(self._update_data)

        # delete
        self.ui.delete_pushButton.clicked.connect(self._delete_data)

        # add
        self.ui.add_pushButton.clicked.connect(self._add_data)

        # query
        self.ui.query_pushButton.clicked.connect(self._do_query)

        # unselect
        self.ui.clear_pushButton.clicked.connect(self._clear)

        # 找到下拉框里应该有的数据并且填入
        self._initialize_table_menu()

    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()

    def _clear(self):
        self.ui.search_comboBox.setCurrentIndex(0)
        self.ui.update_comboBox.setCurrentIndex(0)
        self.ui.delete_comboBox.setCurrentIndex(0)
        self.ui.search_lineEdit.clear()
        self.ui.update_lineEdit.clear()
        self.ui.delete_lineEdit.clear()

    def _initialize_table_menu(self):
        sql = """
            SHOW TABLES
            """
        rows, _ = do_query(sql)

        for row in rows:
            self.ui.table_comboBox.addItem(row[0], row)

    def _adjust_column_widths(self):
        header = self.ui.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(QHeaderView.Stretch)

    def _get_column_name(self):
        self.ui.search_comboBox.clear()
        self.ui.update_comboBox.clear()
        self.ui.delete_comboBox.clear()

        table = self.ui.table_comboBox.currentData()

        self.ui.search_comboBox.addItem('select')
        self.ui.update_comboBox.addItem('select')
        self.ui.delete_comboBox.addItem('select')

        sql = (f"""
            show columns from  daydayup_db2.{table[0]};
            """)
        rows, _ = do_query(sql)
        col = []
        for row in rows:
            col.append(row[0])
            self.ui.search_comboBox.addItem(row[0], row)
            self.ui.update_comboBox.addItem(row[0], row)
            self.ui.delete_comboBox.addItem(row[0], row)
        return col

    def _initialize_table(self):
        """
        Clear the table and set the column headers.
        """
        self.ui.tableWidget.clear()
        table = self.ui.table_comboBox.currentData()
        if not table:
            return

        sql = f"""
            SELECT COUNT(*) FROM {table[0]}
            """
        row_num, _ = do_query(sql)
        self.ui.tableWidget.setRowCount(row_num[0][0])  # 设置表格的行数

        sql = (f"""
            select count(*) from information_schema.columns 
            where table_schema='daydayup_db2' and table_name= '{table[0]}'
            """)
        col_num, _ = do_query(sql)
        self.ui.tableWidget.setColumnCount(col_num[0][0])  # 设置表格的列数

        # 初始化列名
        col = self._get_column_name()
        print(col)
        self.ui.tableWidget.setHorizontalHeaderLabels(col)
        self._enter_data()
        self._adjust_column_widths()

    def _enter_data(self):
        table = self.ui.table_comboBox.currentData()
        sql = (f"""
            SELECT * from {table[0]}
            """
               )
        rows, _ = do_query(sql)

        # Set the class data into the table cells.
        row_index = 0
        for row in rows:
            column_index = 0

            for data in row:
                item = QTableWidgetItem(str(data))
                self.ui.tableWidget.setItem(row_index, column_index, item)
                column_index += 1
            row_index += 1
        self._adjust_column_widths()

    def _search_data(self):
        self.ui.tableWidget.clear()
        table = self.ui.table_comboBox.currentData()
        column = self.ui.search_comboBox.currentData()
        value = self.ui.search_lineEdit.text()

        curr = self.ui.search_comboBox.currentIndex()
        self.ui.tableWidget.setHorizontalHeaderLabels(self._get_column_name())
        self.ui.search_comboBox.setCurrentIndex(curr)

        if not table: return
        if not column or not value:
            self._initialize_table()

        sql = (f"""
            SELECT * FROM {table[0]} WHERE {column[0]} = '{value}';
            """
               )
        rows, _ = do_query(sql)

        # Set the class data into the table cells.
        row_index = 0
        for row in rows:
            column_index = 0

            for data in row:
                item = QTableWidgetItem(str(data))
                self.ui.tableWidget.setItem(row_index, column_index, item)
                column_index += 1
            row_index += 1
        self._adjust_column_widths()

    def _update_data(self):
        table = self.ui.table_comboBox.currentData()
        column = self.ui.search_comboBox.currentData()
        value = self.ui.search_lineEdit.text()

        if not table: return
        if not column or not value:
            self.ui.search_lineEdit.setText('please enter value')
            return

        update_column = self.ui.update_comboBox.currentData()
        update_value = self.ui.update_lineEdit.text()

        conn = make_connection()
        cursor = conn.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        cursor.execute(f'''
            UPDATE {table[0]}
            SET {update_column[0]} = '{update_value}' 
            WHERE {column[0]} = '{value}'
            ''')
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        conn.commit()

        # 这个指令会自动unselect
        self._initialize_table()

    def _delete_data(self):
        table = self.ui.table_comboBox.currentData()
        column = self.ui.delete_comboBox.currentData()
        value = self.ui.delete_lineEdit.text()

        if not table: return
        if not column or not value:
            self.ui.search_lineEdit.setText('please enter value')
            return

        conn = make_connection()
        cursor = conn.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        cursor.execute(f'''
            DELETE FROM {table[0]} WHERE ({column[0]} = '{value}');
            ''')
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')
        conn.commit()

        self._initialize_table()

    def _add_data(self):
        table = self.ui.table_comboBox.currentData()
        if not table: return

        col = self._get_column_name()
        column = ''
        value = ''
        for i in col:
            # 这里column是用的 ` 而不是 '
            column += f'`{i}`,'
            value += 'default,'
        column = column[:-1]
        value = value[:-1]

        conn = make_connection()
        cursor = conn.cursor()
        cursor.execute('SET FOREIGN_KEY_CHECKS = 0;')
        sql = (f'''
            INSERT INTO {table[0]} ({column}) 
            VALUES ({value});
            ''')
        print(sql)
        cursor.execute(sql)
        cursor.execute('SET FOREIGN_KEY_CHECKS = 1;')

        conn.commit()
        self._initialize_table()

    def _do_query(self):
        conn = make_connection()
        cursor = conn.cursor()
        if self.ui.radioButton.isChecked():
            sql = (f'''
                select Track.TrackId, Genre.Name GenreName, MediaType.Name MediatypeName
                from MediaType, Genre, Track
                where Track.GenreId = Genre.GenreId
                and Track.MediaTypeId = MediaType.MediaTypeId
                and Track.TrackId = '{self.ui.lineEdit.text()}';''')
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(['Track Id', 'Genre Name', 'Media Type Name'])
            self._clear_text(1)
        if self.ui.radioButton_2.isChecked():
            sql = (f'''
                select Customer.CustomerId, Customer.FirstName, Track.Name TrackName
                from Customer, Playlist, PlaylistTrack, Track
                where `Playlist`.CustomerId = Customer.CustomerId
                and Playlist.PlaylistId=PlaylistTrack.PlaylistId
                and PlaylistTrack.TrackId = Track.TrackId
                and Customer.CustomerId = '{self.ui.lineEdit_2.text()}';''')
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(['Customer Id', 'First Name', 'Track Name'])
            self._clear_text(2)
        if self.ui.radioButton_3.isChecked():
            sql = (f'''
                select Employee.EmployeeId, Customer.CustomerId, Customer.FirstName, Customer.LastName
                from Customer, Employee
                where Employee.EmployeeId = Customer.SupportRepId
                and Employee.EmployeeId = '{self.ui.lineEdit_3.text()}';''')
            self.ui.tableWidget.setColumnCount(4)
            self.ui.tableWidget.setHorizontalHeaderLabels(['Employee Id', 'Customer Id', 'First Name', 'Last Name'])
            self._clear_text(3)
        if self.ui.radioButton_4.isChecked():
            sql = (f'''
                select Artist.Name ArtistName, Album.Title AlbumTitle, Track.Name TrackName
                from Artist, Album, Track
                where Artist.ArtistId=Album.AlbumId
                and Album.AlbumId = Track.AlbumId
                and Artist.Name = '{self.ui.lineEdit_4.text()}';''')
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(['Artist Name', 'Album Title', 'Track Name'])
            self._clear_text(4)
        if self.ui.radioButton_5.isChecked():
            sql = (f'''
                select Track.Name 'Track Name', Customer.FirstName 'First Name', Customer.LastName 'Last Name'
                from Customer, Invoice, InvoiceLine, Track
                where Customer.CustomerId=Invoice.CustomerId
                and Invoice.InvoiceId = InvoiceLine.InvoiceId
                and InvoiceLine.TrackId = Track.TrackId
                and Track.Name = '{self.ui.lineEdit_5.text()}';''')
            self.ui.tableWidget.setColumnCount(3)
            self.ui.tableWidget.setHorizontalHeaderLabels(['TrackName', 'First Name', 'Last Name'])
            self._clear_text(5)

        self.ui.none_label.setText('Query completed! If it shows an empty table, please try other inputs :)')

        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        self.ui.tableWidget.setRowCount(len(result))

        row_index = 0
        for row in result:
            column_index = 0
            for data in row:
                item = QTableWidgetItem(str(data))  # convert data type
                self.ui.tableWidget.setItem(row_index, column_index, item)
                column_index += 1
            row_index += 1
        self._adjust_column_widths()

    def _clear_text(self, num):
        if num != 1:
            self.ui.lineEdit.clear()
        if num != 2:
            self.ui.lineEdit_2.clear()
        if num != 3:
            self.ui.lineEdit_3.clear()
        if num != 4:
            self.ui.lineEdit_4.clear()
        if num != 5:
            self.ui.lineEdit_5.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = updateDialog()
    form.show_dialog()
    sys.exit(app.exec_())

# %%

# %%

# %%
