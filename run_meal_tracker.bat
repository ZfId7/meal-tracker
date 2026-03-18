@echo off
cd /d D:/projects/meal_tracker
call conda activate meal_tracker
start "" http://127.0.0.1:8080
waitress-serve --host=127.0.0.1 --port=8080 run:app
