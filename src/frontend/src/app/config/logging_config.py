import logging
import re

from src.app.common import signalBus
from collections import defaultdict
log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s\n")


class DeduplicationHandler(logging.Handler):
    def __init__(self, threshold=1000, initial_threshold=2):
        super().__init__()
        self.threshold = threshold
        self.initial_threshold = initial_threshold
        self.messages = defaultdict(int)

    def emit(self, record):
        log_entry = self.format(record)
        filtered_log_entry = self.filter_dynamic_content(log_entry)

        self.messages[filtered_log_entry] += 1
        message_count = self.messages[filtered_log_entry]

        # 当消息首次出现时打印
        if message_count == 1:
            self.deduplicated_emit(log_entry)

        # 当消息出现次数超过初始阈值但未达到总阈值时，不打印，只累计
        elif message_count > self.initial_threshold and message_count < self.threshold:
            pass  # 此处不执行操作，仅累计计数

        # 当消息累计达到总阈值时，再次打印，并重置计数
        elif message_count >= self.threshold:
            log_entry += f" (Repeated {message_count} times)"
            self.deduplicated_emit(log_entry)
            self.messages[filtered_log_entry] = 0

    def filter_dynamic_content(self, log_entry):
        # 假设日志格式的时间戳是以 'YYYY-MM-DD HH:MM:SS,mmm' 格式开头的
        # 此正则表达式将匹配大多数标准ISO格式日期时间
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} - '
        # 使用正则表达式移除日志条目中的时间戳
        return re.sub(timestamp_pattern, '', log_entry)

    def deduplicated_emit(self, log_entry):
        raise NotImplementedError("Subclasses must implement this method")


class QLoggingHandler(DeduplicationHandler):
    def deduplicated_emit(self, log_entry):
        # 使用 Qt 信号发出日志消息
        signalBus.log_message.emit(log_entry)


class StreamDeduplicationHandler(DeduplicationHandler):
    def deduplicated_emit(self, log_entry):
        # 直接打印到标准输出
        print(log_entry)


qt_logging_handler = QLoggingHandler()
stream_handler = StreamDeduplicationHandler()
stream_handler.setFormatter(log_format)

# 设置日志格式和处理器
logging.basicConfig(
    handlers=[
        qt_logging_handler,
        stream_handler],
    level=logging.DEBUG)
qt_logger = logging.getLogger()
