from PySide6.QtCore import QObject

class ApplicationManager(QObject):
    """一个简单的管理器，用于追踪后台任务并在完成后退出应用"""
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.running_workers = []

    def add_worker(self, worker):
        self.running_workers.append(worker)
        # 关键：当任何一个线程结束后，都调用check_quit方法
        worker.finished.connect(lambda: self.on_worker_finished(worker))

    def on_worker_finished(self, worker):
        if worker in self.running_workers:
            self.running_workers.remove(worker)
        self.check_quit()

    def check_quit(self):
        # 检查所有窗口是否都已关闭，并且没有正在运行的线程
        # a.topLevelWidgets() 会返回所有顶级窗口
        all_windows_closed = not any(w.isVisible() for w in self.app.topLevelWidgets())
        
        if all_windows_closed and not self.running_workers:
            print("All windows closed and all workers finished. Quitting.")
            self.app.quit()