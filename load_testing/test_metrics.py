#!/usr/bin/env python3
"""
Скрипт для тестирования метрик FastAPI приложения
"""
import requests
import time
import random

def test_metrics():
    """Генерирует тестовые запросы для создания метрик"""
    base_url = "http://localhost:8000"
    
    print("Тестирование метрик FastAPI...")
    
    # Проверяем доступность метрик
    try:
        metrics_response = requests.get(f"{base_url}/metrics")
        print(f"Метрики доступны: {metrics_response.status_code}")
        print("Первые 500 символов метрик:")
        print(metrics_response.text[:500])
    except Exception as e:
        print(f"Ошибка получения метрик: {e}")
        return
    
    # Генерируем тестовые запросы
    endpoints = ["/", "/auth/login", "/auth/register"]
    
    for i in range(100):
        endpoint = random.choice(endpoints)
        try:
            if endpoint == "/":
                response = requests.get(f"{base_url}{endpoint}")
            else:
                # Для auth endpoints делаем POST запросы (они могут вернуть ошибку, но это нормально)
                response = requests.post(f"{base_url}{endpoint}", json={})
            
            print(f"Запрос {i+1}: {endpoint} -> {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"Ошибка запроса {endpoint}: {e}")
    
    print("\nТестирование завершено!")

if __name__ == "__main__":
    test_metrics()
