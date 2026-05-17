from http.server import BaseHTTPRequestHandler, HTTPServer


class MockServerRequestHandler(BaseHTTPRequestHandler):
    """
    Actual response headers from school server:

        HTTP/2 200
        cache-control: no-cache
        content-type: text/html
        content-encoding: gzip
        last-modified: Tue, 12 May 2026 07:36:42 GMT
        accept-ranges: bytes
        etag: "0a17b13e2e1dc1:0"
        vary: Accept-Encoding
        server: Microsoft-IIS/10.0
        date: Wed, 13 May 2026 17:09:51 GMT
        content-length: 4728
        X-Firefox-Spdy: h2
    """

    def do_GET(self):
        with open("./files/rezultati.htm", encoding="windows-1250") as f:
            content = f.read()

        # No need to include all the headers
        self.send_response(200)
        self.send_header("content-type", "text/html")
        self.send_header("content-length", str(len(content)))
        self.end_headers()

        self.wfile.write(content.encode("windows-1250"))


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8001), MockServerRequestHandler)
    print("Mock server running on http://localhost:8001")
    server.serve_forever()
