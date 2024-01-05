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
    force = request_json["force"] if "force" in request_json else False

    interaction_net = IntarctionNet(url, webdriver_path, binary_location, force)
    logging.info(request_json)
    logging.info(
        f"webdriver_path {webdriver_path}, binary_location {binary_location}, force {force}"
    )
    results = {}
    if request_json is None or "action" not in request_json:
        results["status"] = "error"
        results["error"] = f"Invalid action: {request_json}"
        return jsonify(results)

    match request_json["action"]:
        case "apply":
            weeks = request_json["weeks"] if "weeks" in request_json else 4
            is_last = request_json["is_last"] if "is_last" in request_json else False
            results["data"] = interaction_net.apply(weeks, is_last)
        case "result":
            results["data"] = interaction_net.result()
        case "test":
            results["data"] = interaction_net.test()

    end_time = time.time()
    results["status"] = "success"
    results["time"] = end_time - start_time
    return jsonify(results)
