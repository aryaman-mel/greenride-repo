from flask import Flask, jsonify, request

app = Flask(__name__)

# in-memory sample data
RIDES = [
    {"id": 1, "driver": "Alex", "route": "Waurn Ponds → Burwood", "time": "08:30"},
]

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.get("/rides")
def get_rides():
    return jsonify(RIDES), 200

@app.post("/bookings")
def create_booking():
    data = request.get_json() or {}
    return jsonify({"status": "booked", "data": data}), 201

if __name__ == "__main__":
    # local dev run: python app/app.py
    app.run(host="0.0.0.0", port=8000, debug=True)
# run with: flask --app app.app run --host=0.0.0.0 --port=8000