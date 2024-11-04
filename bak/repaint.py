# def print_to_output(self, text):
#     QMetaObject.invokeMethod(self, "update_output", Qt.QueuedConnection,
#                              Q_ARG(str, text))
#
# @Slot(str)  # Принимаем текст как аргумент слота
# def update_output(self, text):
#     self.output_pane.appendPlainText(text)
#     cursor = self.output_pane.textCursor()
#     cursor.movePosition(QTextCursor.MoveOperation.End)
#     self.output_pane.setTextCursor(cursor)
#     self.output_pane.repaint()
