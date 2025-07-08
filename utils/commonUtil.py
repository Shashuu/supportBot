import os
import yaml
import json

from pathlib import Path

from utils.logger import commonLogger
from constants.constants import FileExt

from utils.cleanser import Cleanser

config = {}

saveFileDict = {}
readFileDict = {}

def getConfig(path):
    if config.get(path):
        return config[path]
    
    try:
        base_config = open(path)
        config[path] = yaml.load(base_config.read(), yaml.SafeLoader)
    except Exception as e:
        print(f"failed while loading from {path} with reason {str(e)}")
        return dict()

    return config[path]

def readFile(fullFilePath, ext):
    if not (ext in readFileDict):
        log.exception(f"undefined ext found {ext} to save the data.")
        return    
    if not fullFilePath.endswith(ext.value):
        fullFilePath = fullFilePath + "." + ext.value
    readFunc = readFileDict[ext]
    return readFunc(fullFilePath)

def saveFile(data, fullFilePath, ext):
    if not (ext in saveFileDict):
        log.exception(f"undefined ext found {ext} to save the data.")
        return
    
    if not fullFilePath.endswith(ext.value):
        fullFilePath = fullFilePath + "." + ext.value
    
    saveFunc = saveFileDict[ext]
    saveFunc(data, fullFilePath)

def _readJSON(fullFilePath, encoding="utf-8"):
    with open(fullFilePath, "r", encoding=encoding) as f:
        return json.load(f)

def _saveJSON(data, fullFilePath, encoding="utf-8"):
    with open(fullFilePath, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def pathConstruct(folder, filename):
    return os.path.join(folder, filename)

def listFilesByDir(folderPath):
    return os.listdir(folderPath)

def retrieveFilesWithExt(listOfFiles, extension):
    return [file for file in listOfFiles if file.lower().endswith(str(extension).lower())]

def getFilesByRelativePaths(dataDir, ext):
    return [pathConstruct(folder=dataDir, filename=file) for file in retrieveFilesWithExt(listOfFiles=listFilesByDir(folderPath=dataDir), extension=ext)]

def getBaseFileNameFromDirPath(fullPath):
    return os.path.basename(fullPath)

def getFileNameWithoutExt(fullPath):
    return Path(fullPath).stem

def cleansedText(*args):
    return  " ".join(args).replace("\n", " ").lower()

def formatCleanseTheRecord(record):
    # basic cleanse
    record = Cleanser.basicCleanse(record)

    # format
    # formattedRecord = Cleanser.format(record)
    
    # cleanse
    # cleansedRecord = Cleanser.cleanse(formattedRecord)
    return record

conf = "config/config.yaml"
c = getConfig(conf)

c["filename"] = c["logpath"]
log = commonLogger(**c)

saveFileDict[FileExt.JSON] = _saveJSON
readFileDict[FileExt.JSON] = _readJSON