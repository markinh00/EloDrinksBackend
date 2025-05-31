from dotenv import load_dotenv
import os
import redis

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")


def redis_connection():
    """
    Create a Redis connection.
    """
    try:
        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            decode_responses=True,
        )
        client.ping()  # Test the connection
        return client
    except redis.ConnectionError as e:
        print(f"Redis connection error: {e}")
        return None


if __name__ == "__main__":
    # Test the Redis connection
    client = redis_connection()
    if client:
        print("Redis connection successful!")
    else:
        print("Failed to connect to Redis.")
