from flask import Flask, request
import os
import time
from dotenv import load_dotenv
from interaction_net.module import IntarctionNet


load_dotenv()
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def execute():
    start_time = time.time()
    request_json = request.get_json(silent=True)
    url = os.environ["URL"]
    webdriver_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "chromedriver"
    )
    debug_mode = True if request_json and "debug_mode" in request_json else False

    interaction_net = IntarctionNet(url, webdriver_path, debug_mode)
    print(f"INFO: {request_json}")
    if request_json and "action" in request_json:
        if request_json["action"] == "apply":
            interaction_net.apply()
        elif request_json["action"] == "result":
            interaction_net.result()
        else:
            return '{ "status": "error", "message": "' + f"Invalid action: {request_json['action']}" + '" }'
    end_time = time.time()
    elapsed_time = end_time - start_time
    elapsed_minutes = int(elapsed_time / 60)
    print("INFO: elasped_minutes: " + f"{elapsed_minutes}")
    return '{ "status": "success", "elapsed_time": ' + f"{elapsed_time}" + ' }'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
