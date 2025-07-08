from utils.commonUtil import (getFilesByRelativePaths, getConfig, pathConstruct, 
                             readFile, getFileNameWithoutExt, saveFile, cleansedText, 
                             formatCleanseTheRecord, getBaseFileNameFromDirPath)
from utils.cleanser import Cleanser
from utils.logger import Logger

from constants.constants import FileExt

from service.embedding.embedGenService import EmbedGen
from service.searcher.searcher import SearcherIndexService

import argparse

parser = argparse.ArgumentParser()

parser.add_argument("--indexDir")
parser.add_argument("--dataDir")
parser.add_argument("--extType")

parser.add_argument("--conf")
parser.add_argument("--embedConf")
parser.add_argument("--indexConf")

args = parser.parse_args()

conf = getConfig(args.conf)
embConf = getConfig(args.embedConf)
indConf = getConfig(args.indexConf)

log = Logger(filename = conf["logFile"])

ext = FileExt(args.extType)
embGenUtil = EmbedGen(**embConf)

# read the base data
listOfFilesByType = dict()
for scrappedType in conf["scrappedType"]:
    dataFolderPath = pathConstruct(args.dataDir, scrappedType)
    listOfFilesByType[scrappedType] = getFilesByRelativePaths(dataFolderPath, ext.value)

startIndex = 1
dataDict = dict()

dd = {"Common Medical Event": ["Member out of pocket", "Limitations, Exceptions, & Other Important Information"],
      "Important Questions": ["Answers", "Why This Matters"],}

planType = {
    "parsedOtherPages_America's_Choice_2500_Gold_SOB (1) (1).json": "PSM Health Plan: 2,500 Plan Option",
    "parsedFirstPage_America's_Choice_2500_Gold_SOB (1) (1).json": "PSM Health Plan: 2,500 Plan Option",
    "parsedOtherPages_America's_Choice_5000_Bronze_SOB (2).json": "PSM Health Plan: 5,000 Plan Option",
    "parsedFirstPage_America's_Choice_5000_Bronze_SOB (2).json": "PSM Health Plan: 5,000 Plan Option",
    "parsedOtherPages_America's_Choice_5000_HSA_SOB (2).json": "PSM Health Plan: 5,000 HSA Plan Option",
    "parsedFirstPage_America's_Choice_5000_HSA_SOB (2).json": "PSM Health Plan: 5,000 HSA Plan Option",
    "parsedOtherPages_America's_Choice_7350_Copper_SOB (1) (1).json": "PSM Health Plan: 7,350 Plan Option",
    "parsedFirstPage_America's_Choice_7350_Copper_SOB (1) (1).json": "PSM Health Plan: 7,350 Plan Option",
}

def getEmbedding(record):
     # generate the embed
    embedding = embGenUtil.getEmbed(record)
    return embedding

# cleanse
for scrappedType, listOfFilepaths in listOfFilesByType.items():
    indexUtil = SearcherIndexService(**indConf, log=log)
    for filepath in listOfFilepaths:
        data = readFile(filepath, ext)
        if scrappedType == "pdf":
            for _, record in data.items():
                planName = planType[getBaseFileNameFromDirPath(filepath)]
                for eve in dd.keys():
                    if eve in record:
                        pretext = (record[eve] + " " + record["Services You May Need"]) if eve == "Common Medical Event" else record[eve]
                        #print(pretext)

                        for col in dd[eve]:
                            recordData = cleansedText(planName, pretext, col, record[col])
                            embedding = getEmbedding(formatCleanseTheRecord(recordData))

                            # index the embed
                            indexUtil.index(embedding=embedding, id=startIndex)

                            dataDict[startIndex] = recordData
                            startIndex += 1
        else:
            for que, ans in data.items():
                recordData = cleansedText(que, ans)
                embedding = getEmbedding(formatCleanseTheRecord(recordData))

                # index the embed
                indexUtil.index(embedding=embedding, id=startIndex)

                dataDict[startIndex] = recordData
                startIndex += 1

    indexName = pathConstruct(args.indexDir, 
                                scrappedType + "." + FileExt.INDEX.value)
    # print(indexName)
    indexUtil.save(indexName)

saveFile(dataDict, pathConstruct(args.indexDir, conf["dataMap"]), FileExt.JSON)