from qtpy.QtCore import Signal, QRegularExpression
from qtpy.QtGui import QPainter, QColor, QRegularExpressionValidator
from qtpy.QtWidgets import QLineEdit
from .country_dropdown import CountryDropdown


class PhoneLineEdit(QLineEdit):

    # Events
    focus_in = Signal()
    focus_out = Signal()

    def __init__(self, parent=None):
        """Create a new PhoneLineEdit instance

        :param parent: the parent widget
        """

        super(PhoneLineEdit, self).__init__(parent)

        # Connected country dropdown
        self.__country_dropdown = None
        self.__border_color_current = None
        self.__border_width = 0
        self.textChanged.connect(self.text_changed)
        
        # Set validator to only allow numbers and spaces as input
        self.setValidator(QRegularExpressionValidator(QRegularExpression('[0-9 ]*')))

    def set_format(self, phone_format: str):
        self.phone_format = phone_format
        self.separator_positions = []
        self.total_digits = 0

        # Registra le posizioni dei separatori e conta le cifre
        for i, c in enumerate(phone_format):
            if c != '0':
                self.separator_positions.append((i, c))
            else:
                self.total_digits += 1


    def text_changed(self, text: str):
        self.set_format(self.__country_dropdown.getPhoneFormat())
        digits = ''.join(filter(str.isdigit, text))[:self.total_digits]
        formatted = ''
        digit_index = 0

        for i in range(len(self.phone_format)):
            if any(pos == i for pos, _ in self.separator_positions):
                sep = next(sep for pos, sep in self.separator_positions if pos == i)
                formatted += sep
            elif digit_index < len(digits):
                formatted += digits[digit_index]
                digit_index += 1
            else:
                break

        # Mantiene la posizione del cursore dopo la formattazione
        cursor_pos = self.cursorPosition()+1
        self.blockSignals(True)
        self.setText(formatted)
        self.blockSignals(False)
        self.setCursorPosition(min(cursor_pos, len(formatted)))

    def paintEvent(self, event):
        """Method that gets called every time the widget needs to be updated.
        Everything related to widget graphics happens here.

        :param event: event sent by PyQt
        """

        super().paintEvent(event)

        # Draw inside border to separate the LineEdit from connected dropdown
        if self.__country_dropdown and self.__border_color_current:
            painter = QPainter(self)
            painter.setPen(self.__border_color_current)
            x = self.__country_dropdown.width()

            for i in range(self.__border_width):
                painter.drawLine(x + i, 0, x + i, self.height() - 1)

    def focusInEvent(self, event):
        """Method that gets called every time the widget gains focus

        :param event: event sent by PyQt
        """

        super().focusInEvent(event)
        self.focus_in.emit()

    def focusOutEvent(self, event):
        """Method that gets called every time the widget loses focus

        :param event: event sent by PyQt
        """

        super().focusOutEvent(event)
        self.focus_out.emit()

    def getCountryDropdown(self) -> CountryDropdown:
        """Get the current country dropdown

        :return: country dropdown
        """

        return self.__country_dropdown

    def __dropdown_hide(self):
        self.text_changed(self.text())

    def setCountryDropdown(self, country_dropdown: CountryDropdown):
        """Set the country dropdown

        :param country_dropdown: new country dropdown
        """

        self.__country_dropdown = country_dropdown
        self.__country_dropdown.hide_popup.connect(self.__dropdown_hide)

    def getCurrentBorderColor(self) -> QColor:
        """Get the current border color

        :return: current border color
        """

        return self.__border_color_current

    def setCurrentBorderColor(self, color: QColor):
        """Set the current border color

        :param color: new border color
        """

        self.__border_color_current = color
        self.update()

    def getBorderWidth(self) -> int:
        """Get the current border width

        :return: current border width
        """

        return self.__border_width

    def setBorderWidth(self, width: int):
        """Set the current border width

        :param width: new border width
        """

        self.__border_width = width
        self.update()
