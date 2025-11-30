import sys
import sqlite3
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QTableWidgetItem, QDialog


class AddEditCoffeeForm(QDialog):
    def __init__(self, coffee_id=None):
        super(AddEditCoffeeForm, self).__init__()
        uic.loadUi('addEditCoffeeForm.ui', self)
        self.coffee_id = coffee_id
        self.setup_ui()
        if coffee_id:
            self.load_coffee_data()

    def setup_ui(self):
        self.buttonBox.accepted.connect(self.save_coffee)
        self.buttonBox.rejected.connect(self.reject)

    def load_coffee_data(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM coffee WHERE id = ?", (self.coffee_id,))
        record = cursor.fetchone()
        if record:
            self.nameLineEdit.setText(record[1])
            self.roastLineEdit.setText(record[2])
            self.typeLineEdit.setText(record[3])
            self.descriptionTextEdit.setPlainText(record[4])
            self.priceSpinBox.setValue(record[5])
            self.volumeSpinBox.setValue(record[6])
        connection.close()

    def save_coffee(self):
        name = self.nameLineEdit.text()
        roast = self.roastLineEdit.text()
        coffee_type = self.typeLineEdit.text()
        description = self.descriptionTextEdit.toPlainText()
        price = self.priceSpinBox.value()
        volume = self.volumeSpinBox.value()

        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()

        if self.coffee_id:
            cursor.execute("""
                UPDATE coffee
                SET name = ?, roast_level = ?, grind_type = ?,
                    flavor_description = ?, price = ?, package_volume = ?
                WHERE id = ?
            """, (name, roast, coffee_type, description, price, volume, self.coffee_id))
        else:
            cursor.execute("""
                INSERT INTO coffee (name, roast_level, grind_type, flavor_description, price, package_volume)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, roast, coffee_type, description, price, volume))

        connection.commit()
        connection.close()
        self.accept()


class CoffeeApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(CoffeeApp, self).__init__()
        uic.loadUi('main.ui', self)
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        self.addButton.clicked.connect(self.add_coffee)
        self.editButton.clicked.connect(self.edit_coffee)

    def load_data(self):
        connection = sqlite3.connect('coffee.sqlite')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM coffee")
        records = cursor.fetchall()
        self.tableWidget.setRowCount(len(records))
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels([
            "ID", "Название сорта", "Степень обжарки",
            "Молотый/в зернах", "Описание вкуса", "Цена", "Объем упаковки"
        ])
        for i, row in enumerate(records):
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        connection.close()

    def add_coffee(self):
        dialog = AddEditCoffeeForm()
        if dialog.exec():
            self.load_data()

    def edit_coffee(self):
        selected_rows = self.tableWidget.selectedItems()
        if selected_rows:
            row = selected_rows[0].row()
            coffee_id = int(self.tableWidget.item(row, 0).text())
            dialog = AddEditCoffeeForm(coffee_id)
            if dialog.exec():
                self.load_data()
        else:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите запись для редактирования")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec())
