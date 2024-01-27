"""
https://aka.ms/vs/17/release/vc_redist.x64.exe onnx需要的库
"""

from concurrent.futures import ThreadPoolExecutor

from line_profiler_pycharm import profile
from my_insightface.insightface.app.camera import camera_read_done, camera_task
from my_insightface.insightface.app.detector import detect_task
from my_insightface.insightface.app.drawer import streaming_event, draw2web_task
from my_insightface.insightface.app.identifier import identifier_task
from web.velzon.socketio_app import socketio_app


# from memory_profiler import profile


def task_done_callback(future):
    print(f"\nTask completed. Result: {future.result()}")


@profile
def main():
    with ThreadPoolExecutor(max_workers=24) as executor:
        try:
            # 提交任务到线程池
            future1 = executor.submit(camera_task.run)
            future2 = executor.submit(detect_task.run)
            future3 = executor.submit(identifier_task.run)
            future4 = executor.submit(draw2web_task.run)
            future5 = executor.submit(socketio_app.run,
                                      debug=False, port=8088, use_reloader=False)
            # 为每个任务添加回调
            future1.add_done_callback(task_done_callback)
            future2.add_done_callback(task_done_callback)
            future3.add_done_callback(task_done_callback)
            future4.add_done_callback(task_done_callback)
            future5.add_done_callback(task_done_callback)

            # 打印网站入口
            print("http://localhost:8088/")

            quit_text = input("\nPress Enter to quit: ")
            if quit_text == "":
                raise KeyboardInterrupt
        except KeyboardInterrupt as e:
            print("exception:", e)
        finally:
            print("sleep 45s")
            camera_read_done.set()
            print("camera_read_done")
            streaming_event.clear()
            print("streaming_event.clear()")
            identifier_task.stop_milvus()
            socketio_app.stop_thread()
            print("socketio.stop()")
            print("all done")


if __name__ == "__main__":
    main()
