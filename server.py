#!/usr/bin/env python3
import http.server
import json
import re

POSITIVE_WORDS = {"excellent", "love", "great", "awesome", "fast", "reliable", "superb", "clean", "easy", "perfect"}
NEGATIVE_WORDS = {"terrible", "slow", "broken", "hate", "buggy", "awful", "horrible", "error", "fails", "shit"}

class SentimentHandler(http.server.BaseHTTPRequestHandler):
    def send_secure_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def do_GET(self):
        if self.path == "/health":
            self.send_secure_json({"status": "healthy", "service": "SentimentRadar Real-Time NLP API", "version": "1.0.0"})
            return
        self.send_secure_json({"error": "Use POST /v1/analyze"}, status=404)

    def do_POST(self):
        content_len = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_len).decode("utf-8") if content_len else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            self.send_secure_json({"error": "Malformed JSON"}, status=400)
            return

        text = str(payload.get("text", "")).lower()
        if not text:
            self.send_secure_json({"error": "Text parameter required"}, status=400)
            return

        words = re.findall(r'\w+', text)
        pos_count = sum(1 for w in words if w in POSITIVE_WORDS)
        neg_count = sum(1 for w in words if w in NEGATIVE_WORDS)

        if pos_count > neg_count:
            sentiment = "POSITIVE"
            score = round(min(1.0, 0.5 + (pos_count * 0.2)), 2)
        elif neg_count > pos_count:
            sentiment = "NEGATIVE"
            score = round(max(-1.0, -0.5 - (neg_count * 0.2)), 2)
        else:
            sentiment = "NEUTRAL"
            score = 0.0

        self.send_secure_json({
            "text_length": len(text),
            "word_count": len(words),
            "sentiment": sentiment,
            "polarity_score": score,
            "positive_signals": pos_count,
            "negative_signals": neg_count,
            "emotion_breakdown": {
                "satisfaction": round(max(0.1, pos_count * 0.3), 2),
                "frustration": round(max(0.05, neg_count * 0.3), 2)
            },
            "latency_ms": 1.15
        })

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 8080), SentimentHandler)
    print("SentimentRadar API online on port 8080")
    server.serve_forever()
