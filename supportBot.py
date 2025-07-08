from flask import Flask, request
from http import HTTPStatus

from utils.commonUtil import getConfig
from utils.logger import Logger
from utils.requestUtil import ReqHandler, buildURL, getURLs
from utils.responseUtil import build_response

from service.support.supportService import SupportService
from service.generator.answerGenService import AnswerGen

import argparse

parser = argparse.ArgumentParser()

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


parser.add_argument("--conf")
args = parser.parse_args()

conf = getConfig(args.conf)

log = Logger(conf["logpath"])

embedURL = buildURL(**conf["embService"])
searchURL = getURLs(conf["searchService"])

reqHandler = ReqHandler()
answerHandler = AnswerGen(**conf["QAService"])

supportBot = SupportService(
    reqHandler= reqHandler, embGenURL=embedURL, 
    searchURL=searchURL, answerHandler=answerHandler, 
    threshold=conf["threshold"] ,log=log)

app = Flask(__name__)

@app.route("/help", methods=["POST"])
def query():
    try:
        req = request.json
        data = req["query"]
        answer, cand = supportBot.getSupport(data)
        # return build_response(HTTPStatus.OK, {"result": answer, "cand": cand})
        return build_response(HTTPStatus.OK, {"result": answer})
    except Exception as e:
        log.exception(f"failed to process with reason {str(e)}")
        return build_response(HTTPStatus.INTERNAL_SERVER_ERROR, dict())

if __name__ == '__main__':
    # TODO: check the dependent services are live and running.
    app.run(host=conf["host"], port=int(conf["port"]))