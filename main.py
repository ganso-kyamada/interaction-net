from flask import jsonify
import os
import time
import logging
import functions_framework
from interaction_net.module import IntarctionNet


@functions_framework.http
def execute(request):
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()
    request_json = request.get_json(silent=True)
    url = os.environ["URL"]
    webdriver_path = os.getcwd() + "/bin/chromedriver"
    binary_location = os.getcwd() + "/bin/headless-chromium"

    interaction_net = IntarctionNet(url, webdriver_path, binary_location)
    logging.info(request_json)
    logging.info(f"webdriver_path {webdriver_path}, binary_location {binary_location}")
    results = {}
    if request_json and "action" in request_json:
        if request_json["action"] == "apply":
            results["data"] = interaction_net.apply()
        elif request_json["action"] == "result":
            results["data"] = interaction_net.result()
        elif request_json["action"] == "test":
            results["data"] = interaction_net.test()
        else:
            results["status"] = "error"
            results["error"] = "Invalid action: " + request_json["action"]
    end_time = time.time()
    results["status"] = "success"
    results["time"] = end_time - start_time
    return jsonify(results)
