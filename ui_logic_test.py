import pytest
from unittest.mock import patch, Mock, call, MagicMock
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from UI import Ui_MainWindow
from ui_logic import setup_ui_logic, start_data_processing, reset_all_fields, open_file_browser


# 1. 创建 QApplication 实例的 fixture
@pytest.fixture(scope='module')
def app():
    app = QApplication([])
    yield app
    app.exit()


# 2. 创建 Ui_MainWindow 实例的 fixture
@pytest.fixture
def ui(app):
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    setup_ui_logic(ui, MainWindow)
    MainWindow.show()
    yield ui
    MainWindow.close()


def test_open_file_browser_select_tx0_files(ui):
    # 模拟 QFileDialog.getOpenFileNames 的返回值
    with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileNames', return_value=(['test.tx0'], '')):
        open_file_browser(ui.textEditProcessedTxtPreview, tx0=True)
        assert 'test.tx0' in ui.textEditProcessedTxtPreview.toPlainText()


def test_start_data_processing_without_files(ui):
    global global_tx0_input_folder, global_selected_temperature_file

    # 测试两个文件都未选择的情况
    with patch.dict('builtins.__dict__', {'global_tx0_input_folder': None, 'global_selected_temperature_file': None}):
        with patch('builtins.print') as mock_print, \
                patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value='') as mock_dialog, \
                patch('data_processor.convert_tx0_to_txt') as mock_convert, \
                patch('data_processor.filter_temperature_data_by_date') as mock_filter, \
                patch('data_processor.calibrate_resistivity') as mock_calibrate:
            start_data_processing(ui)

            expected_calls = [
                call(f"Debug: global_tx0_input_folder = {global_tx0_input_folder}"),
                call(f"Debug: global_selected_temperature_file = {global_selected_temperature_file}"),
                call("Please use the 'Browser' button to select tx0 files first.")
            ]

            assert mock_print.mock_calls == expected_calls, f"Expected calls: {expected_calls}, but got: {mock_print.mock_calls}"

    # 测试只选择了 tx0 文件的情况
    with patch.dict('builtins.__dict__',
                    {'global_tx0_input_folder': "dummy_path", 'global_selected_temperature_file': None}):
        with patch('builtins.print') as mock_print, \
                patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value='') as mock_dialog, \
                patch('data_processor.convert_tx0_to_txt') as mock_convert, \
                patch('data_processor.filter_temperature_data_by_date') as mock_filter, \
                patch('data_processor.calibrate_resistivity') as mock_calibrate:
            start_data_processing(ui)

            expected_calls = [
                call(f"Debug: global_tx0_input_folder = dummy_path"),
                call(f"Debug: global_selected_temperature_file = {global_selected_temperature_file}"),
                call("Please use the 'Browser' button to select the temperature file first.")
            ]

            assert mock_print.mock_calls == expected_calls, f"Expected calls: {expected_calls}, but got: {mock_print.mock_calls}"


def test_start_data_processing_with_files(ui):
    """测试在选择了文件后的数据处理流程"""
    # 模拟选择了 tx0 文件和温度文件
    global global_tx0_input_folder, global_selected_temperature_file
    global_tx0_input_folder = "dummy_folder_path"
    global_selected_temperature_file = "dummy_temp_file.txt"

    ui.textEditProcessedTxtPreview.setText("test.tx0")
    ui.textEditProcessedTempPreview.setText("temperature.txt")

    with patch('PyQt5.QtWidgets.QFileDialog.getExistingDirectory', return_value="output_dir"), \
         patch('data_processor.convert_tx0_to_txt') as mock_convert, \
         patch('data_processor.filter_temperature_data_by_date') as mock_filter, \
         patch('data_processor.calibrate_resistivity') as mock_calibrate:
        start_data_processing(ui)
        mock_convert.assert_called_once()
        mock_filter.assert_called_once()
        mock_calibrate.assert_called_once()


def test_reset_all_fields(ui):
    """测试所有字段的重置功能"""
    # 预设一些测试值
    ui.startXLineEdit.setText("10")
    ui.startZLineEdit.setText("20")
    ui.endXLineEdit.setText("30")
    ui.endZLineEdit.setText("40")
    ui.qualityLineEdit.setText("50")
    ui.areaLineEdit.setText("60")
    ui.LambdaLineEdit.setText("70")
    ui.IterationLineEdit.setText("80")
    ui.dPhiLineEdit.setText("90")
    ui.checkBox.setChecked(True)

    # 调用 reset_all_fields 进行重置
    reset_all_fields(ui)

    # 验证所有字段是否重置为 0 或清空
    assert ui.startXLineEdit.text() == "0"
    assert ui.startZLineEdit.text() == "0"
    assert ui.endXLineEdit.text() == "0"
    assert ui.endZLineEdit.text() == "0"
    assert ui.qualityLineEdit.text() == "0"
    assert ui.areaLineEdit.text() == "0"
    assert ui.LambdaLineEdit.text() == "0"
    assert ui.IterationLineEdit.text() == "0"
    assert ui.dPhiLineEdit.text() == "0"
    assert not ui.checkBox.isChecked()

    # 清理文本框
    assert ui.textEditProcessedTxtPreview.toPlainText() == ""
    assert ui.textEditProcessedTempPreview.toPlainText() == ""


def test_exit_application(app, ui):
    """测试退出应用程序"""
    with patch.object(QApplication, 'quit') as mock_quit:
        ui.actionExit.trigger()
        mock_quit.assert_called_once()


# 执行测试
if __name__ == '__main__':
    pytest.main()
