from flask import Flask, request
from http import HTTPStatus

from service.searcher.searcher import SearcherIndexService

from utils.commonUtil import getConfig, pathConstruct, readFile
from utils.logger import Logger
from utils.responseUtil import build_response
from constants.constants import FileExt

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--conf")
parser.add_argument("--port")
parser.add_argument("--index")
parser.add_argument("--dataMap")
parser.add_argument("--lp")
args = parser.parse_args()

conf = getConfig(args.conf)
dataMap = readFile(args.dataMap, FileExt.JSON)

log = Logger(pathConstruct(args.lp, conf["logFile"]))

embedService = SearcherIndexService(**conf, indexPath= args.index, log=log)

app = Flask(__name__)

@app.route("/healthcheck", methods=["POST"])
def ping():
    return build_response(HTTPStatus.OK, {"ping": "pong"})

@app.route("/search", methods=["POST"])
def search():
    try:
        req = request.json
        embedding = req["embedding"]
        scoreList, idList = embedService.search(embedding)
        resultList = []
        #print(scoreList, idList)
        for idx in range(len(scoreList[0])):
            #print(scoreList[0][idx], idList[0][idx])
            resultList.append(
                {
                    "id": int(idList[0][idx]),
                    "score": float(scoreList[0][idx]),
                    "text": dataMap[str(idList[0][idx])]
                }
            )
        return build_response(HTTPStatus.OK, resultList)
    except Exception as e:
        log.exception(f"failed to process with reason {str(e)}")
        return build_response(HTTPStatus.INTERNAL_SERVER_ERROR, dict())

if __name__ == '__main__':
    app.run(host=conf["host"], port=int(args.port)) 