# Калькулятор

Портативный калькулятор для Windows с интерфейсом на Tkinter. Для запуска из исходников нужны Python 3.10 или новее и Tkinter; сторонние библиотеки приложению не требуются.

Операции выполняются с обычным математическим приоритетом: сначала скобки, затем умножение и деление, после них сложение и вычитание. Скобки можно вводить кнопками или с клавиатуры. Незакрытые скобки при нажатии `=`, лишняя закрывающая скобка и пустые скобки считаются ошибкой; для сброса нажмите `C` или `Esc`. Между числом и открывающей скобкой подразумевается умножение.

## Запуск из исходников

Из папки проекта выполните:

```powershell
python calculator.py
```

## Сборка в `.exe`

Сборку нужно выполнять в Windows на компьютере с Python 3.10+ и Tkinter. PyInstaller собирает приложение для текущей операционной системы и не предназначен для кросс-сборки Windows-приложений из другой ОС.

В PowerShell из папки проекта выполните:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install pyinstaller
.\.venv\Scripts\python.exe -m PyInstaller --noconfirm --clean --onefile --windowed --name Calculator --distpath dist --workpath build --specpath build calculator.py
```

Готовый файл появится здесь:

```text
dist\Calculator.exe
```

`--onefile` собирает программу в один исполняемый файл, а `--windowed` запускает её без консольного окна. PyInstaller нужен только для сборки и не является зависимостью запускаемого приложения.

## Тесты

```powershell
python -m unittest -v test_calculator_engine
```
