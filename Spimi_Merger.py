import ast
from os import listdir
import json
from collections import OrderedDict

class Spimi_Merger:
    """
    This class is to do the merge part of spimi
    """
    BlockFilePath = '/Users/lekangdu/Downloads/40051703-A2/SPIMI-BM25/DISK'

    FirstLineOfOriginData = {} # dictionary { blockID, {term, posting list{}}}
    FinalIndex = {} # dict{ term, posting list{} }
    FinalIndexFile = 0

    # open block files first
    # and get each block's first data
    def openBlocksAndGetFirstLine(self):
        """
        This function is to open block files and get the first line of it
        """
        BlockFiles = []
        blockID = ''
        files = listdir(self.BlockFilePath)
        for file in files:
            if str(file).find("Block") != -1:
                BlockFiles.append(self.BlockFilePath + '/' + file)
        file_handles = [open(f) for f in BlockFiles]
        for f in file_handles:
            fileName = str(f)
            blockID = fileName[fileName.find('Block') + 5:int(fileName.find('txt') - 1)]
            firstLine = f.readline()
            tempDic = {}
            if firstLine != None and firstLine.split(':')[1] != None:
                pl = firstLine.split(':')[1]
                tempList = firstLine.split(':')[1]
                tempDic[firstLine.split(':')[0]] = tempList
                self.FirstLineOfOriginData[blockID] = tempDic
                print(type(tempList))
                for i in tempList:
                    print(type(i))


        # merge
        counter = 0
        while self.FirstLineOfOriginData:

            # write total 25000 terms into final index file
            if counter >= 25000:
                with open('/Users/lekangdu/Downloads/40051703-A2/SPIMI-BM25/Index/' + str(self.FinalIndexFile) + '.txt', 'a+') as f:
                    for iterm in self.FinalIndex:
                        f.write(iterm + ":")
                        f.write(str(self.FinalIndex[iterm]) + '\n')
                    self.FinalIndexFile += 1
                    self.FinalIndex.clear()
                    counter = 0


            # get the block which has lowest term
            lowestBlockId = self.getLowestTerm()[0]
            # print(lowestBlockId)
            # get the cooresponding lowest term
            lowestTerm = self.getLowestTerm()[1]


            # put into final index dictionary, {term,list}
            if lowestTerm not in self.FinalIndex:
                self.FinalIndex[lowestTerm] = []
                self.FinalIndex[lowestTerm] = eval(self.FirstLineOfOriginData[lowestBlockId][lowestTerm])
                counter += 1
            else:
                temp = []
                temp = self.FinalIndex[lowestTerm] + ast.literal_eval(self.FirstLineOfOriginData[lowestBlockId][lowestTerm])
                self.FinalIndex[lowestTerm] = temp

            # load next term for block whose term had been merged
            # remove the term which just be merged in FirstLineOfOriginData
            self.FirstLineOfOriginData[lowestBlockId].pop(lowestTerm)

            # iterate file_handles to find the file which just been merged
            next_line = ""
            next_term = ""
            next_list = ""
            for i in file_handles:
                cur_fileName = str(i)
                Cur_blockID = cur_fileName[cur_fileName.find('Block') + 5:int(cur_fileName.find('txt') - 1)]
                if lowestBlockId == Cur_blockID:
                    next_line = i.readline()
                    if next_line != '' and len(next_line.split(':')) > 1:
                        next_term = next_line.split(':')[0]
                        next_list = next_line.split(':')[1]


            # load this term into FirstLineOfOriginData
            if next_line != '':
                temp_dic = {}
                temp_dic[next_term] = next_list
                self.FirstLineOfOriginData[lowestBlockId] = temp_dic
            else:
                self.FirstLineOfOriginData.pop(lowestBlockId)

        if not self.FirstLineOfOriginData:
            with open('/Users/lekangdu/Downloads/40051703-A2/SPIMI-BM25/Index/' + str(self.FinalIndexFile) + '.txt', 'a+') as f:
                for iterm in self.FinalIndex:
                    f.write(iterm + ":")
                    f.write(str(self.FinalIndex[iterm]) + '\n')
                self.FinalIndexFile += 1
                self.FinalIndex.clear()
                counter = 0

    def openBlocksAndGetFinalIndex(self):
        """
        This fuunction is to get the index and
        save to files
        """
        BlockFiles = []
        blockID = ''
        files = listdir(self.BlockFilePath)
        for file in files:
            if str(file).find("Block") != -1:
                BlockFiles.append(self.BlockFilePath + '/' + file)
        file_handles = [open(f) for f in BlockFiles]
        count = 0
        for fi in file_handles:
            block = json.load(fi)
            for k, v in block.items():
                if not k in self.FinalIndex:
                    self.FinalIndex[k] = v
                else:
                    self.FinalIndex[k].update(v)
        # sort
        Sorted_PostingList = sorted(self.FinalIndex)

        # write into files
        temp_dict = OrderedDict()
        for i in Sorted_PostingList:
            if count >= 25000:
                with open('/Users/lekangdu/Downloads/40051703-A2/SPIMI-BM25/Index/' + str(self.FinalIndexFile) + '.txt', 'a+') as f:
                    json.dump(temp_dict, f)
                count = 0
                temp_dict = {}
                self.FinalIndexFile += 1
            temp_dict[i] = self.FinalIndex[i]
            count += 1
        with open('/Users/lekangdu/Downloads/40051703-A2/SPIMI-BM25/Index/' + str(self.FinalIndexFile) + '.txt', 'a+') as f:
            json.dump(temp_dict, f)
        count = 0
        temp_dict = {}
        self.FinalIndexFile += 1


    def getLowestTerm(self):
        """
        This function is to get the lowest term of each block
        :return: lowestTerm_Block,LowestString
        """
        lowestTerm_Block = ''
        LowestString = ''
        temp_dict = {} # {blockID,term}
        for i in self.FirstLineOfOriginData:
            # lowestTerm_Block = i
            for j in self.FirstLineOfOriginData[i]:
                temp_dict[i] = j
        # print(lowestTerm_Block + ' ^ ' + LowestString)
        for i in temp_dict:
            LowestString = temp_dict[i]
            lowestTerm_Block = i
        for i in temp_dict:
            if LowestString > temp_dict[i]:
                LowestString = temp_dict[i]
                lowestTerm_Block = i
        return [lowestTerm_Block,LowestString]

    def reCreatePostingList(self,string):
        print()

