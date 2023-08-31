setlocal

call .venv\Scripts\activate

cd src
echo "in src directory"
@REM call waitress-serve --port=8080 --call setup.py:create_app
call python start_app.py

call deactivate

endlocal