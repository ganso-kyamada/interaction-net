from flask import jsonify
import os
import time
import logging
import functions_framework
from interaction_net.module import InteractionNet


@functions_framework.http
def execute(request):
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()
    logging.info(f"Start time: {start_time}")
    request_json = request.get_json(silent=True)
    logging.info(request_json)

    results = {}
    if request_json is None or "action" not in request_json:
        results["status"] = "error"
        results["error"] = f"Invalid action: {request_json}"
        return jsonify(results)

    url = os.environ["URL"]
    webdriver_path = os.getcwd() + "/bin/chromedriver"
    binary_location = os.getcwd() + "/bin/headless-chromium"
    interaction_net = InteractionNet(url, webdriver_path, binary_location)
    logging.info(f"webdriver_path {webdriver_path}, binary_location {binary_location}")

    match request_json["action"]:
        case "apply":
            weeks = request_json["weeks"] if "weeks" in request_json else 4
            is_retry = request_json["is_retry"] if "is_retry" in request_json else False
            results["data"] = interaction_net.apply(weeks, is_retry)
        case "result":
            is_retry = request_json["is_retry"] if "is_retry" in request_json else False
            results["data"] = interaction_net.result(is_retry)
        case "cancel":
            results["data"] = interaction_net.cancel()
        case "test":
            results["data"] = interaction_net.test()

    end_time = time.time()
    results["status"] = "success"
    results["time"] = end_time - start_time
    return jsonify(results)
