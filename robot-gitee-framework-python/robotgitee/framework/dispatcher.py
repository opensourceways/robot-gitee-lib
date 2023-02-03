from http.server import HTTPServer, BaseHTTPRequestHandler
import signal
import threading

from robotgitee import logutil


class _Webhook(BaseHTTPRequestHandler):
    def do_POST(self):
        if not self.path.startswith("/gitee-hook"):
            self.send_error(400, "Bad Request: unknown path")
            return

        if self.headers.get("User-Agent") != "Robot-Gitee-Access":
            self.send_error(400, "Bad Request: unknown User-Agent Header")
            return

        event_type = self.headers.get("X-Gitee-Event")
        if event_type == "":
            self.send_error(400, "Bad Request: Missing X-Gitee-Event Header")
            return

        uuid = self.headers.get("X-Gitee-Timestamp")
        if uuid == "":
            self.send_error(
                400, "Bad Request: Missing X-Gitee-Timestamp Header",
            )

            return

        data = self.rfile.read(int(self.headers.get("content-length")))

        log = logutil.new_logutil()

        log.field("event_type", event_type).field("uuid", uuid)

        self.server.dispatch(event_type, uuid, data, log)

        self.send_response(201, "done")
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.wfile.write(
            bytes("Event received. Have a nice day.", encoding="utf-8"),
        )

    def do_GET(self):
        if self.path != "/":
            self.send_error(400, "Bad Request: unknown path")
            return

        self.send_response_only(200, "done")


class _Dispatcher(HTTPServer):
    def __init__(self, server_address, handlers):
        self.handlers = handlers
        self.wg = _WaitGroup()

        super().__init__(server_address, _Webhook)

    def run(self):
        logutil.info("start server, listen on: %s:%d" % self.server_address)

        signal.signal(signal.SIGINT, self.exit)

        t = threading.Thread(target=self.serve_forever)
        t.daemon = True
        t.start()
        # wait the web server to exit
        t.join()

        self.server_close()
        logutil.info("web server exits")

        # wait threads of event handler to exit
        self.wg.wait()

    def exit(self, num, frame):
        log = logutil.new_logutil()
        log.field("num", num).field("frame", str(frame)).info(
            "recieve signal to shutdown the server",
        )

        self.shutdown()

        log.info("server is shutdown")

    def dispatch(self, event_type, uuid, payload, log):
        if event_type not in self.handlers:
            return

        self.wg.add()

        t = threading.Thread(
            target=self.do,
            args=(self.handlers[event_type], payload, log),
        )

        t.start()

    def do(self, handle, payload, log):
        try:
            handle(payload, log)
        except Exception as e:
            log.error(str(e))
        finally:
            self.wg.done()


class _WaitGroup(object):
    """_WaitGroup is like Go sync.WaitGroup.

    Without all the useful corner cases.
    """
    def __init__(self):
        self.count = 0
        self.cv = threading.Condition()

    def add(self, n=1):
        self.cv.acquire()
        self.count += n
        self.cv.release()

    def done(self):
        self.cv.acquire()
        self.count -= 1
        if self.count <= 0:
            self.cv.notify_all()
        self.cv.release()

    def wait(self):
        self.cv.acquire()
        while self.count > 0:
            self.cv.wait()
        self.cv.release()
