"""
Health check endpoints для мониторинга состояния приложения.
"""
import asyncio
import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from prometheus_client import Counter, Gauge, Histogram
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.dao_dep import get_session_without_commit

router = APIRouter()

# Prometheus метрики для health checks
health_check_counter = Counter(
    'health_check_requests_total',
    'Total number of health check requests',
    ['endpoint', 'status']
)

health_check_duration = Histogram(
    'health_check_duration_seconds',
    'Time spent on health checks',
    ['endpoint']
)

database_connection_gauge = Gauge(
    'database_connection_status',
    'Database connection status (1=healthy, 0=unhealthy)'
)

database_response_time_gauge = Gauge(
    'database_response_time_seconds',
    'Database response time in seconds'
)

system_cpu_gauge = Gauge(
    'system_cpu_percent',
    'System CPU usage percentage'
)

system_memory_gauge = Gauge(
    'system_memory_percent',
    'System memory usage percentage'
)

system_disk_gauge = Gauge(
    'system_disk_percent',
    'System disk usage percentage'
)


async def check_database_connection(session: AsyncSession) -> Dict[str, Any]:
    """
    Проверка подключения к базе данных.
    
    Args:
        session: Асинхронная сессия базы данных
        
    Returns:
        Dict с информацией о состоянии БД
    """
    start_time = time.time()
    
    try:
        # Простой запрос для проверки подключения
        result = await session.execute(text("SELECT 1 as health_check"))
        row = result.fetchone()
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Обновляем Prometheus метрики
        database_response_time_gauge.set(response_time)
        
        if row and row[0] == 1:
            database_connection_gauge.set(1)  # Здоровое состояние
            return {
                "status": "healthy",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
        else:
            database_connection_gauge.set(0)  # Нездоровое состояние
            return {
                "status": "unhealthy",
                "error": "Unexpected database response",
                "response_time_ms": round(response_time * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        database_connection_gauge.set(0)  # Нездоровое состояние
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


async def check_system_resources() -> Dict[str, Any]:
    """
    Проверка системных ресурсов.
    
    Returns:
        Dict с информацией о системных ресурсах
    """
    try:
        import psutil
        
        # Получаем информацию о системе
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Обновляем Prometheus метрики
        system_cpu_gauge.set(cpu_percent)
        system_memory_gauge.set(memory.percent)
        system_disk_gauge.set((disk.used / disk.total) * 100)
        
        return {
            "status": "healthy",
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "timestamp": datetime.now().isoformat()
        }
    except ImportError:
        # psutil не установлен
        return {
            "status": "limited",
            "message": "System monitoring unavailable (psutil not installed)",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"System resources check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/health", tags=["Health"])
async def basic_health_check() -> Dict[str, Any]:
    """
    Базовая проверка состояния приложения.
    
    Returns:
        Базовая информация о состоянии сервиса
    """
    with health_check_duration.labels(endpoint="basic").time():
        health_check_counter.labels(endpoint="basic", status="success").inc()
        
        return {
            "status": "healthy",
            "service": "FastAPI Starter Build",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "uptime": "Service is running"
        }


@router.get("/health/detailed", tags=["Health"])
async def detailed_health_check(
    session: AsyncSession = Depends(get_session_without_commit)
) -> Dict[str, Any]:
    """
    Детальная проверка состояния приложения включая БД и системные ресурсы.
    
    Args:
        session: Асинхронная сессия базы данных
        
    Returns:
        Детальная информация о состоянии всех компонентов
    """
    with health_check_duration.labels(endpoint="detailed").time():
        try:
            # Запускаем проверки параллельно
            db_check_task = asyncio.create_task(check_database_connection(session))
            system_check_task = asyncio.create_task(check_system_resources())
            
            # Ждем завершения всех проверок
            db_status, system_status = await asyncio.gather(
                db_check_task, 
                system_check_task,
                return_exceptions=True
            )
            
            # Обрабатываем исключения
            if isinstance(db_status, Exception):
                db_status = {
                    "status": "error",
                    "error": str(db_status),
                    "timestamp": datetime.now().isoformat()
                }
            
            if isinstance(system_status, Exception):
                system_status = {
                    "status": "error", 
                    "error": str(system_status),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Определяем общий статус
            overall_status = "healthy"
            if (db_status.get("status") not in ["healthy", "limited"] or 
                system_status.get("status") not in ["healthy", "limited"]):
                overall_status = "unhealthy"
                health_check_counter.labels(endpoint="detailed", status="unhealthy").inc()
            else:
                health_check_counter.labels(endpoint="detailed", status="healthy").inc()
            
            return {
                "status": overall_status,
                "service": "FastAPI Starter Build",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "checks": {
                    "database": db_status,
                    "system": system_status
                }
            }
            
        except Exception as e:
            health_check_counter.labels(endpoint="detailed", status="error").inc()
            logger.error(f"Detailed health check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Health check failed: {str(e)}"
            )


@router.get("/health/ready", tags=["Health"])
async def readiness_check(
    session: AsyncSession = Depends(get_session_without_commit)
) -> Dict[str, Any]:
    """
    Проверка готовности приложения к обработке запросов (readiness probe).
    
    Args:
        session: Асинхронная сессия базы данных
        
    Returns:
        Информация о готовности сервиса
        
    Raises:
        HTTPException: Если сервис не готов к работе
    """
    with health_check_duration.labels(endpoint="readiness").time():
        try:
            # Проверяем подключение к БД
            db_status = await check_database_connection(session)
            
            if db_status.get("status") != "healthy":
                health_check_counter.labels(endpoint="readiness", status="not_ready").inc()
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail={
                        "status": "not_ready",
                        "reason": "Database connection failed",
                        "database": db_status,
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            health_check_counter.labels(endpoint="readiness", status="ready").inc()
            return {
                "status": "ready",
                "service": "FastAPI Starter Build",
                "timestamp": datetime.now().isoformat(),
                "database": db_status
            }
            
        except HTTPException:
            raise
        except Exception as e:
            health_check_counter.labels(endpoint="readiness", status="error").inc()
            logger.error(f"Readiness check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    "status": "not_ready",
                    "reason": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )


@router.get("/health/live", tags=["Health"])
async def liveness_check() -> Dict[str, Any]:
    """
    Проверка жизнеспособности приложения (liveness probe).
    
    Returns:
        Информация о том, что приложение живо
    """
    with health_check_duration.labels(endpoint="liveness").time():
        health_check_counter.labels(endpoint="liveness", status="alive").inc()
        
        return {
            "status": "alive",
            "service": "FastAPI Starter Build", 
            "timestamp": datetime.now().isoformat()
        }


@router.get("/health/metrics", tags=["Health"])
async def health_metrics() -> Dict[str, Any]:
    """
    Endpoint для получения метрик здоровья в JSON формате.
    Дополняет стандартный /metrics endpoint Prometheus.
    
    Returns:
        Метрики здоровья в JSON формате
    """
    with health_check_duration.labels(endpoint="metrics").time():
        health_check_counter.labels(endpoint="metrics", status="success").inc()
        
        # Получаем текущие значения метрик безопасным способом
        try:
            db_status = database_connection_gauge._value._value if hasattr(database_connection_gauge, '_value') else 0
            db_response_time = database_response_time_gauge._value._value if hasattr(database_response_time_gauge, '_value') else 0
            cpu_percent = system_cpu_gauge._value._value if hasattr(system_cpu_gauge, '_value') else 0
            memory_percent = system_memory_gauge._value._value if hasattr(system_memory_gauge, '_value') else 0
            disk_percent = system_disk_gauge._value._value if hasattr(system_disk_gauge, '_value') else 0
        except (AttributeError, TypeError):
            # Если не можем получить значения, возвращаем 0
            db_status = db_response_time = cpu_percent = memory_percent = disk_percent = 0
        
        return {
            "database": {
                "connection_status": db_status,
                "response_time_seconds": db_response_time
            },
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent
            },
            "timestamp": datetime.now().isoformat()
        }