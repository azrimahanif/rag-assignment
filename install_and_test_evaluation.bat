@echo off
echo Installing evaluation system dependencies...
pip install -r evaluation\requirements.txt
echo.
echo Testing evaluation system...
cd service2
python evaluation\test_evaluation.py
pause