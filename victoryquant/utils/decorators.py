"""
装饰器工具
"""
import time
import functools
from typing import Callable, Any
from .logger import get_logger

logger = get_logger()


def retry(max_attempts: int = 3, delay: float = 1.0, 
          exceptions: tuple = (Exception,)):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(
                        f"函数 {func.__name__} 第 {attempt + 1} 次执行失败: {e}"
                    )
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
            
            logger.error(
                f"函数 {func.__name__} 执行失败，已重试 {max_attempts} 次"
            )
            raise last_exception
        
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        logger.info(f"函数 {func.__name__} 执行时间: {execution_time:.4f} 秒")
        
        return result
    
    return wrapper


def log_call(func: Callable) -> Callable:
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        logger.debug(f"调用函数 {func.__name__}, 参数: {args}, 关键字参数: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"函数 {func.__name__} 返回: {result}")
        return result
    
    return wrapper


def cache_result(func: Callable) -> Callable:
    cache = {}
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        key = str(args) + str(sorted(kwargs.items()))
        
        if key in cache:
            logger.debug(f"从缓存返回 {func.__name__} 结果")
            return cache[key]
        
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    return wrapper
