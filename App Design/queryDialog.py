import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QApplication, QTableWidgetItem, QHeaderView, QMessageBox
from mydbutils_2 import do_query, make_connection


class queryDialog(QDialog):
    """
    The query dialog.
    """

    def __init__(self):
        """
        Load the UI and initialize its components.
        """
        super().__init__()

        # Load the dialog components.
        self.ui = uic.loadUi('query_dialog.ui')

        # clear
        self.ui.clear_button.clicked.connect(self.clear)

        # music submit
        self.ui.music_submit_button.clicked.connect(self._do_music_query)

        # sales submit
        self.ui.sales_submit_button.clicked.connect(self._do_sales_query)

        self._initial_menu()

    def show_dialog(self):
        """
        Show this dialog.
        """
        self.ui.show()

    def _adjust_column_widths(self):
        header = self.ui.tableWidget.horizontalHeader();
        header.setSectionResizeMode(QHeaderView.ResizeToContents)

    def clear(self):
        self.ui.start_age_lineEdit.clear()
        self.ui.end_age_lineEdit.clear()
        self.ui.age_comboBox.setCurrentIndex(0)
        self.ui.gender_comboBox.setCurrentIndex(0)

        self.ui.city_comboBox.setCurrentIndex(0)
        self.ui.state_comboBox.setCurrentIndex(0)
        self.ui.country_comboBox.setCurrentIndex(0)
        self.ui.week_comboBox.setCurrentIndex(0)
        self.ui.month_comboBox.setCurrentIndex(0)
        self.ui.year_comboBox.setCurrentIndex(0)

    def _enter_data(self, result):
        self.ui.tableWidget.setRowCount(len(result))

        row_index = 0
        for row in result:
            column_index = 0
            for data in row:
                item = QTableWidgetItem(str(data))
                self.ui.tableWidget.setItem(row_index, column_index, item)
                column_index += 1
            row_index += 1
        self._adjust_column_widths()

    def _initial_menu(self):
        # City
        sql = ("SELECT City FROM Location GROUP BY City;")
        rows, _ = do_query(sql)
        for row in rows:
            self.ui.city_comboBox.addItem(row[0], row)
        # State
        sql = ("SELECT State FROM Location GROUP BY State;")
        rows, _ = do_query(sql)
        for row in rows:
            self.ui.state_comboBox.addItem(row[0], row)
        # Country
        sql = ("SELECT Country FROM Location GROUP BY Country;")
        rows, _ = do_query(sql)
        for row in rows:
            self.ui.country_comboBox.addItem(row[0], row)

    def _do_music_query(self):
        conn = make_connection()
        cursor = conn.cursor()

        gender_index = self.ui.gender_comboBox.currentIndex()
        if gender_index == 0:
            gender = ''
        elif gender_index == 1:
            gender = 'AND Gender = \'f\''
        else:
            gender = 'AND Gender = \'m\''

        start = self.ui.start_age_lineEdit.text()
        end = self.ui.end_age_lineEdit.text()
        if not start or not end:
            self.ui.start_age_lineEdit.clear()
            self.ui.end_age_lineEdit.clear()
            age_index = self.ui.age_comboBox.currentIndex()
            if age_index == 0:
                start, end = 0, 100
            elif age_index == 1:
                start, end = 16, 35
            elif age_index == 2:
                start, end = 35, 60
            else:
                start, end = 60, 100

        sql = (f'''
                SELECT GenreName Genre, COUNT(TrackKey) 'Num of Track'
                FROM Preference_Fact_Table, Customer, Genre
                WHERE Preference_Fact_Table.GenreKey = Genre.GenreKey
                AND Preference_Fact_Table.CustomerKey = Customer.CustomerKey
                {gender} AND {start} <= Age AND Age < {end}
                GROUP BY GenreName
                ORDER BY COUNT(TrackKey) DESC;''')
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(['Genre', 'Num of Track'])

        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        self._enter_data(result)

    def _do_sales_query(self):
        conn = make_connection()
        cursor = conn.cursor()

        city_index = self.ui.city_comboBox.currentIndex()
        state_index = self.ui.state_comboBox.currentIndex()
        country_index = self.ui.country_comboBox.currentIndex()

        week_index = self.ui.week_comboBox.currentIndex()
        month_index = self.ui.month_comboBox.currentIndex()
        year_index = self.ui.year_comboBox.currentIndex()

        year = ['None', 2009, 2010]

        curr = []  # 放到select的columns
        value = []  # 放到where的特定值
        group = []
        if week_index != 0:
            curr.append('DayOfWeek')
            if week_index == 8:
                group.append('DayOfWeek')
            else:
                value.append(f'AND DayOfWeek = {week_index}')
        if month_index != 0:
            curr.append('Month')
            if month_index == 13:
                group.append('Month')
            else:
                value.append(f'AND Month = {month_index}')
        if year_index != 0:
            curr.append('Year')
            if year_index == 3:
                group.append('Year')
            else:
                value.append(f'AND Year = {year[year_index]}')
        if city_index != 0:
            curr.append('City')
            if city_index == 1:
                group.append('City')
            else:
                value.append(f'AND City = \'{self.ui.city_comboBox.currentData()[0]}\'')
        if state_index != 0:
            curr.append('State')
            if state_index == 1:
                group.append('State')
            else:
                value.append(f'AND State = \'{self.ui.state_comboBox.currentData()[0]}\'')
        if country_index != 0:
            curr.append('Country')
            if country_index == 1:
                group.append('Country')
            else:
                value.append(f'AND Country = \'{self.ui.country_comboBox.currentData()[0]}\'')

        if len(group) == 0:
            self.box = QMessageBox().information(
                None, "ERROR",
                '''Please try other input!''',
                QMessageBox.Yes)
            return

        col = ['Total Sales']
        col.extend(curr)
        self.ui.tableWidget.setColumnCount(len(col))
        self.ui.tableWidget.setHorizontalHeaderLabels(col)

        # select columns
        curr_str = ''
        for i in curr:
            curr_str += ', ' + i

        value_str = ''
        for i in value:
            value_str += ' ' + i

        group_str = 'GROUP BY '
        for i in group:
            group_str += ' ' + i + ','

        sql = (f'''
                SELECT ROUND(sum(unitPrice), 2) 'Total Sales'{curr_str}
                FROM Sales_Fact_Table, Location, Timedetail
                WHERE Sales_Fact_Table.TimeKey = Timedetail.TimeKey 
                AND Sales_Fact_Table.LocationKey = Location.LocationKey AND Sales_Fact_Table.LocationKey = Location.LocationKey {value_str}
                {group_str[:-1]}
                ORDER BY sum(unitPrice) DESC;''')

        print(sql)
        cursor.execute(sql)
        result = cursor.fetchall()
        self._enter_data(result)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = queryDialog()
    form.show_dialog()
    sys.exit(app.exec_())
#%%
