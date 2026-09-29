@echo off

cd /d C:\Users\akula\OneDrive\Desktop\Rajanna_DairyFarm\rdf_project

if not exist logs mkdir logs

C:\Users\akula\OneDrive\Desktop\Rajanna_DairyFarm\venv\Scripts\python.exe manage.py generate_milk_deliveries >> logs\milk_deliveries.log 2>&1