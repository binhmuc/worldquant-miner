from typing import List, Tuple
import random

class RetryStrategy:
    def __init__(self, max_attempts: int):
        self.max_attempts = max_attempts
        self.attempts = 0

    def retry(self) -> bool:
        if self.attempts < self.max_attempts:
            self.attempts += 1
            return True
        else:
            return False

def optimize_retry_strategy(max_attempts: int, strategy: RetryStrategy) -> List[Tuple[int, bool]]:
    results = []
    for attempt in range(max_attempts):
        success = strategy.retry()
        result = (attempt + 1, success)
        results.append(result)
    return results