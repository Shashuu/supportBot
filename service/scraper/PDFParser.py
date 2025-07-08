from service.scraper.interface import Parser
import pdfplumber

import pandas as pd
import numpy as np

from utils.commonUtil import getFilesByRelativePaths, pathConstruct, saveFile, getBaseFileNameFromDirPath, getFileNameWithoutExt
from constants.constants import FileExt

import time

class PDFParser(Parser):
    def __init__(self, conf, log, *args, **kwargs):
        self.pdfFiles = getFilesByRelativePaths(dataDir=conf["dataDir"], ext=FileExt.PDF.value)
        self.headers = conf["headers"]
        self.firstPageHeaders = conf["firstPageColumns"]
        self.otherPagesHeaders = conf["otherPagesColumns"]
        self.conf = conf
        
        self.faqs = dict()
        self._page_map = dict()
        
        self.log = log
    
    def get_parser_obj(self, filepath):
        return pdfplumber.open(filepath)
    
    def save_faq(self):
        pass

    def build_faq(self):
        pass

    def get_index(self, pdfPageData):
        try:
            hl = [i for i in pdfPageData[0][0] if i is not None]
            if max(hl):
                return 0
            return 1
        except Exception as e:
            return 1

    def extract_table(self, pdfPageData):
        listOfTables = list()
        for pdfPage in pdfPageData.pages:
            listOfTables.append(pdfPage.extract_tables())
        return listOfTables
    
    def filter_data(self, pdfData, startIndex):
        toBeConsidered = list()
        headerSet = False
        for line in pdfData[startIndex]:
            if line and ((line[0] in self.headers) or (line[1] in self.headers)):
                headerSet = True
            if headerSet:
                toBeConsidered.append(line)
        return toBeConsidered
    
    def get_cleansed_data_df(self, df):
        colsConsidered = list()
        for col in df:
            if not df[col].isna().all():
                colsConsidered.append(col)
        df = df[colsConsidered]
        return df
    
    def get_filtered_data_df(self, pageInfoRecords, startIndex):
        # filter the data
        filteredData = self.filter_data(pageInfoRecords, startIndex)
        df = pd.DataFrame(filteredData, columns=[str(i) for i in range(max([len(ln) for ln in filteredData]))])
        df.replace('', np.nan, inplace=True)
        return df
    
    def format_data(self, df):
        df.fillna('', inplace=True)
        
        # second col, concat the rows into one.
        cols = list(df.columns)
        flattenedVals = list()
        helperString = ''
        for i in list(df[cols[-1]])[::-1]:
            if i and len(str(i)):
                helperString = str(i) + ' ' + helperString
                helperString += ''
                if helperString[0].isupper():
                    flattenedVals.append(helperString)
                    helperString = ''
                else:
                    flattenedVals.append('')
            else:
                flattenedVals.append('')


        df[cols[-1]] = flattenedVals[::-1]

        df['merged'] = df.apply(lambda row: row[cols[0]] if row[cols[0]] > row[cols[1]] else row[cols[1]], axis=1)

        return df[['merged']]
    
    def pre_process_page_data(self, filteredDataRecordsDF):
        cols = list(filteredDataRecordsDF.columns)
        listOfDfs = list()
        for colIndex in range(0, len(cols), 2):
            ddf = self.format_data(filteredDataRecordsDF[cols[colIndex: colIndex+2]])
            listOfDfs.append(ddf)
        return pd.concat(listOfDfs, axis=1)

    def pre_process_first_page_data(self, pageInfoRecords):
       df = self.get_filtered_data_df(pageInfoRecords, self.get_index(pageInfoRecords))
       df = self.get_cleansed_data_df(df)
       return self.pre_process_page_data(df)

    def pre_process_non_first_page_data(self, pageInfoRecords):
       mainDF = self.get_filtered_data_df(pageInfoRecords[0], self.get_index(pageInfoRecords[0]))
       temDF = pd.DataFrame()
       ind = 1
       for pageInfo in pageInfoRecords[1:-1]:
           ind += 1
           if pageInfo:
               curDF = self.get_filtered_data_df(pageInfo, self.get_index(pageInfo))[1:]
               temDF = pd.concat([temDF, curDF])

       mainDF = pd.concat([mainDF, temDF])
       mainDF = self.get_cleansed_data_df(mainDF)
       return self.pre_process_page_data(mainDF)

    def parse_content(self, filepath, ind):
        # extract the tables
        # pre process the data
        # finalise the data in a map<ques, map<ans, matter>>
        # firstPage = False
        pdfData = self.get_parser_obj(filepath = filepath)
        listOfExtTables = self.extract_table(pdfData)
        # listOfExtTables       >> list of tables
        # listOfExtTables[0]    >> page with formats
        # listOfExtTables[0][0] >> tabular lines
        frontDF = self.pre_process_first_page_data(listOfExtTables[0])
        frontDF.replace('', np.nan, inplace=True)
        frontDF.dropna(how='all', inplace=True)
        frontDF.ffill(inplace=True)
        frontDF[1:].to_csv(f'data/scraper/out/pdf/firstPage{ind}.csv', index=False)
        
        othersDF = self.pre_process_non_first_page_data(listOfExtTables[1:])
        othersDF.replace('', np.nan, inplace=True)
        othersDF.dropna(how='all', inplace=True)
        othersDF.ffill(inplace=True)
        othersDF[1:].to_csv(f'data/scraper/out/pdf/otherPages{ind}.csv', index=False)

        frontDF.columns = self.firstPageHeaders
        othersDF.columns = self.otherPagesHeaders

        frontDF = frontDF.reset_index()
        othersDF = othersDF.reset_index()

        frontDF = frontDF[self.firstPageHeaders]
        othersDF = othersDF[self.otherPagesHeaders]

        inFileNameWithoutExt = getFileNameWithoutExt(filepath)

        frontDFRecords = dict()
        for idx, row in frontDF[1:].iterrows():
            frontDFRecords[str(idx)] = row.to_dict()
        outFileName = pathConstruct(self.conf['outDir'], self.conf['frontPagePrefix']).format(inFileNameWithoutExt)
        saveFile(frontDFRecords, outFileName, FileExt.JSON)
        
        othersDFRecords = dict()
        for idx, row in othersDF[1:].iterrows():
            othersDFRecords[str(idx)] = row.to_dict()
        outFileName = pathConstruct(self.conf['outDir'], self.conf['otherPagePrefix']).format(inFileNameWithoutExt)
        saveFile(othersDFRecords, outFileName, FileExt.JSON)

        return ((frontDF, othersDF))
    
    def start(self):
        for ind, pdfFile in enumerate(self.pdfFiles):
            self.parse_content(filepath=pdfFile, ind=ind)
