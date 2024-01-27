import queue
import threading
import uuid
from time import sleep

import numpy as np

from src.boostface.app.common import LightImage
from src.boostface.app.detector import Detector


# Let's assume LightImage and Detector are defined in the provided paths.
# Since I can't import your custom modules, I'll use placeholder implementations.


class ImageGenerator:
    def generate_light_image(self, pixels=5000000):
        side_length = int(np.sqrt(pixels / 3))
        image_array = np.random.randint(0, 256, (side_length, side_length, 3), dtype=np.uint8)
        return LightImage(nd_arr=image_array), uuid.uuid4()


class Producer(threading.Thread):
    def __init__(self, task_queue, images, results, results_lock):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.images = images
        self.results = results
        self.results_lock = results_lock

    def run(self):
        for img, img_id in self.images:
            self.task_queue.put((img, img_id))  # Send the image and its UUID
            # Wait for the result
            result_received = False
            while not result_received:
                sleep(0.01)  # Avoid busy waiting
                with self.results_lock:  # Ensure thread-safe access to results
                    if img_id in self.results:
                        result_received = True
                        print(f"Result received for image {img_id}")
                        self.results.pop(img_id)  # Remove the result from the dictionary
        self.task_queue.put(None)  # Signal the consumer to exit


class Consumer(threading.Thread):
    def __init__(self, task_queue, results, results_lock):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.detector = Detector()
        self.results = results
        self.results_lock = results_lock

    def run(self):
        while True:
            task = self.task_queue.get()
            if task is None:
                break  # Exit signal
            img, img_id = task
            result = self.detector(img)  # Process the image
            with self.results_lock:  # Ensure thread-safe access to results
                self.results[img_id] = result  # Store the result with the UUID as key


if __name__ == '__main__':
    task_queue = queue.Queue()
    results = {}
    results_lock = threading.Lock()
    num_images = 500  # Set a smaller number for testing

    image_generator = ImageGenerator()
    images = [image_generator.generate_light_image() for _ in range(num_images)]

    # Create Producer and Consumer threads
    producer = Producer(task_queue, images, results, results_lock)
    consumer = Consumer(task_queue, results, results_lock)

    # Start the threads
    producer.start()
    consumer.start()

    # Wait for both threads to complete
    producer.join()
    consumer.join()

    print("All tasks complete.")
