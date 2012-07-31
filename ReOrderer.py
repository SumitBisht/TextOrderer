import wx
import os
import random
from docx import *
import sys
'''
This is the main class that provides both the UI and logic for the text randomization.
'''
class ReOrderer(wx.Frame):

    def __init__(self):
        self.splitDelim = '\n'
        self.questions = {}
        wx.Frame.__init__(self, None, -1, 'Question Randomizer', size=(600, 400))
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(101, "&Open", "Open a text file containing tests")
        self.Bind(wx.EVT_MENU, self.OnFileSelect, id=101)
        menu.Append(102, "&Close", "Exit this application")
        self.Bind(wx.EVT_MENU, self.OnCloseWindow, id=102)
        menubar.Append(menu, "&File")
        menu = wx.Menu()
        menu.Append(201, "&Set Order", "Set the default ordering of tests")
        self.Bind(wx.EVT_MENU, self.OnUseOrder, id=201)
        menu.Append(202, "&Randomize", "Randomize ordering of tests")
        self.Bind(wx.EVT_MENU, self.OnRandomize, id=202)
        menubar.Append(menu, "&Edit")
        self.SetMenuBar(menubar)

        self.myStatusBar = wx.StatusBar(id=wx.NewId(), name='myStatusBar', parent=self, style=wx.ST_SIZEGRIP)
        self.statusLabel = wx.StaticText(self.myStatusBar,-1,'',(5, 3))
        self.statusLabel.ForegroundColour = 'Red'
        swiss_font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        self.statusLabel.SetFont(swiss_font)
        
        self.selectedFileText = wx.TextCtrl(self, -1, "No File Selected", size=(500,25), style = wx.TE_READONLY)
        self.FileSelector = wx.Button(self, wx.NewId(), "Select File", size=(100, 25))
        self.Bind(wx.EVT_BUTTON, self.OnFileSelect, self.FileSelector)
        childsizer = wx.BoxSizer(wx.HORIZONTAL)
        childsizer.Add(self.selectedFileText, 1, wx.EXPAND)
        childsizer.Add(self.FileSelector, 0 , wx.EXPAND|wx.ALIGN_LEFT)
        mainsizer.Add(childsizer)

        self.orderField = wx.TextCtrl(self, -1, "", size = (600, 25))
        orderFieldChildSizer = wx.BoxSizer(wx.HORIZONTAL)
        orderFieldChildSizer.Add(self.orderField, 1, wx.EXPAND)
        mainsizer.Add(orderFieldChildSizer)

        self.content = wx.TextCtrl(self, style=wx.NO_BORDER|wx.TE_MULTILINE, size=(600,400));
        mainsizer.Add(self.content)
        
        self.save = wx.Button(self, -1, "Save Test")
        self.Bind(wx.EVT_BUTTON, self.OnSaveToFile, self.save)
        self.run = wx.Button(self, -1, "Randomize")
        self.Bind(wx.EVT_BUTTON, self.OnRandomize, self.run)
        self.orderuser = wx.Button(self, -1, "Use Order")
        self.Bind(wx.EVT_BUTTON, self.OnUseOrder, self.orderuser)
        self.save.Disable()
        self.run.Disable()
        self.orderuser.Disable()
        
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.save, 3, wx.EXPAND)
        buttonsizer.Add(self.run, 2, wx.EXPAND)
        buttonsizer.Add(self.orderuser, 3, wx.EXPAND)
        mainsizer.Add(buttonsizer)
        self.SetSizerAndFit(mainsizer)
        self.SetMinSize(self.GetSize())
    
    def OnSaveToFile(self, event):
        fileChoices = "MS-Word 2007 |*.docx |Text file |*.txt |All files |*.* "
        savedFile = wx.FileDialog (None, "Save file as...", os.getcwd(), "", fileChoices, wx.SAVE)
        if savedFile.ShowModal() == wx.ID_OK:
            if savedFile.__contains__('docx'):
                None
            else:
                opFile = open(savedFile.GetPath(), 'w')
                opFile.write(self.content.GetValue())
                opFile.flush()
                opFile.close()

    def OnFileSelect(self, event):
        fileChoices = "MS-Word 2007 |*.docx|Text file |*.txt|All files|*.*"
        extractedFile = wx.FileDialog (None, "Choose a file containing the test Questions", os.getcwd(), "", fileChoices, wx.OPEN)
        
        if extractedFile.ShowModal() == wx.ID_OK:
            selectedFileName = extractedFile.GetPath()
            self.selectedFileText.SetValue(selectedFileName)
            questions = self.readDocx(selectedFileName)
            self.setVarFields(questions)
            
            self.save.Enable()
            self.run.Enable()
            self.orderuser.Enable()
        extractedFile.Destroy()

    def readDocx(self, filename):
        questionList = []
        qText = ''
        document = opendocx(filename)
        paragraphs = getdocumenttext(document)
        
        for question in paragraphs:
            qText +=question
            if question.__contains__('(D)'):
                questionList.append(qText)
                qText = ''
        return questionList
        
    def setVarFields(self, qList):
        order = ''
        self.content.Clear()
        for quest in qList:
            questn = quest.strip()
            question = questn.split('(A)')[0]
            self.content.WriteText('\n' + question)
            answer = questn[len(question):].split('\t')
            for line in answer:
                if line.__contains__('(') and line.__contains__(')'):
                    self.content.WriteText('\n')
                self.content.WriteText(line)
            
            self.content.WriteText('\n')
            qNum = question.split('.')[0]
            order+= qNum+' ,'
            self.questions[qNum] = quest
        self.orderField.SetValue('')
        self.orderField.SetValue(order[:-2])

    # Provides for randomization of the questions, is not dependent on any prior user input
    def OnRandomize(self, event):
        self.UpdateQuestionDict()
        current_order = self.orderField.GetValue().split(',')
        
        if len(current_order) == 0:
            self.GiveError('Nothing to randomize')
            return
        newContent = ""
        random.shuffle(current_order)
        
        self.content.Clear()
        
        for num in current_order:
            question = self.questions.pop(num)
            newContent += question.split('.')[0].strip()+' ,'
            self.WriteQuestion(question)
        self.orderField.SetValue('')
        self.orderField.SetValue(newContent[:-2])

    # Uses the order field to populate the rest of the test
    def OnUseOrder(self, event):
        self.UpdateQuestionDict()
        self.content.Clear()
        current_order = self.orderField.GetValue().split(',')
        if len(current_order) == 0:
            self.GiveError('Nothing to randomize')
            return
        for qnum in current_order:
            qnum = qnum.strip()
            self.WriteQuestion(self.questions[qnum])
        #self.setVarFields(questionList)
        
    def UpdateQuestionDict(self):
        reorder = []

        questions = self.content.GetValue().split('\n')
        question = ''
        questionList = []
        for line in questions:
            question+=line
            if len(line)==0 and question != '':
                reorder.append(question.split('.')[0].strip())
                questionList.append(question)
                question = ''
        for num in reorder:
            self.questions[num] = questionList.pop(0)
    
    #A common method to write the question passed on to it in an orderly manner.  
    def WriteQuestion(self, question):
        qn = question.split('(A)')[0]
        ans = question[len(qn):]
        self.content.WriteText(qn + '\n')
        ans = ans.split('(')
        for a in ans:
            if len(a)<1:
                continue
            self.content.WriteText('('+ a + '\n')
        self.content.WriteText('\n')

    # Provides error dialogs in a resuable manner.
    # Is based on the presence of loaded file contents
    def GiveError(self, actionPerformed):
        dlg=wx.MessageDialog(self, 'Please load text file containing Questions', actionPerformed, wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.CenterOnScreen()
        dlg.Destroy()

    def OnCloseWindow(self, event):
        contents = self.content.GetValue()
        if len(contents) != 0:
            msg = wx.MessageBox("Are you sure to exit?", 'Text ReOrderer',wx.YES_NO | wx.ICON_QUESTION)
            if msg == wx.YES:
                self.Destroy()
            else:
                return
        self.Destroy()

class App(wx.App):
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect=True, filename=None)

    def OnInit(self):
        self.frame = ReOrderer()
        self.frame.Show(True)
        return True

if __name__ == '__main__':
        app = App()
        app.MainLoop()