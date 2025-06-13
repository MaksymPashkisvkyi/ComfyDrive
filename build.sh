#!/bin/bash

echo "📦 Встановлюємо залежності..."
pip install -r requirements.txt

echo "🛠 Виконуємо міграції..."
python manage.py migrate --noinput

echo "🎨 Збираємо статичні файли..."
python manage.py collectstatic --noinput

