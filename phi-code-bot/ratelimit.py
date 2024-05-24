import time


def sliding_window_rate_limit(user_id, window_size, limit, redis_connection) -> bool:
    """
    Implements a sliding window rate limiter.

    Args:
    user_id (str): The user identifier.
    window_size (int): The window size in seconds.
    limit (int): The maximum number of allowed requests in the window.
    redis_connection (redis.Redis): Connection to Redis.

    Returns:
    bool: True if the request is within the rate limit, False otherwise.

    """
    
    current_time = int(time.time()*1000)
    key = f"ratelimit:{user_id}"

    with redis_connection.pipeline() as pipe:
        # Remove all timestamps outside the current window
        pipe.zremrangebyscore(key, 0, current_time - window_size * 1000)
        # Get the number of requests in the current window
        pipe.zcard(key)
        # Add the current timestamp to the set of timestamps
        pipe.zadd(key, {current_time: current_time})
        # Set the expiry on the key to match the duration of the window
        pipe.expire(key, window_size)
        # Execute the pipeline
        results = pipe.execute()

    num_requests = results[1]

    return num_requests <= limit
