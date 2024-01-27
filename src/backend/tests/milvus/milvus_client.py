from time import sleep

from src.boostface.db import MilvusClient


def main():
    face_client = MilvusClient()
    try:
        sleep(100)
    except KeyboardInterrupt:
        print("Interrupted by user, shutting down")
    finally:
        face_client.shut_down()


if __name__ == '__main__':
    main()
