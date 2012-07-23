import wx
import os
import random
'''
This is the main class that provides both the UI and logic for the text randomization.
'''
class ReOrderer(wx.Frame):

    def __init__(self):
        self.splitDelim = '\n'
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
        self.Bind(wx.EVT_MENU, self.OnQuestionOrderSelect, id=201)
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
        fileChoices = "Text file |*.txt|All files|*.*"
        savedFile = wx.FileDialog (None, "Save file as...", os.getcwd(), "", fileChoices, wx.SAVE)
        if savedFile.ShowModal() == wx.ID_OK:
            opFile = open(savedFile.GetPath(), 'w')
            opFile.write(self.content.GetValue())
            opFile.flush()
            opFile.close()

    def OnRandomize(self, event):
        paperContent = self.content.GetValue()
        current_order = self.orderField.GetValue().split(',')
        
        if len(paperContent) == 0:
            self.GiveError('Nothing to randomize')
            return
        splits = self.splitRawData(paperContent)
        newContent = ""
        
        for split in splits:
            random.shuffle(split)
            self.content.SetValue("")
            for item in split:
                #q_number= item.split('\n')[0].split('.')[0]
                while(current_order[0].strip()=='*'):
                    newContent += self.extra_contents.pop(0)
                    newContent += self.splitDelim
                    current_order = current_order[1:]
                
                newContent += item
                newContent += self.splitDelim
                current_order = current_order[1:]
            
        self.content.SetValue(newContent.rstrip(self.splitDelim))
        self.OnQuestionOrderSelect(event)
        
    def splitRawData(self, inputData):
        questions = self.SplitContentIntoQuestions(inputData, True)
        current_order = self.orderField.GetValue().split(',')
        questionLists = []
        prevNumber = -1
        list = []
        for questn in current_order:
            try:
                number = int(questn)
                if number < prevNumber:
                    questionLists.append(list)
                    list = []
                    
                list.append(questions.pop(0)) 
                prevNumber = number
            except Exception as err:
                if len(list) > 0:
                    questionLists.append(list)
                    list = []
                
        questionLists.append(list)
        return questionLists

    def OnFileSelect(self, event):
        fileChoices = "Text file |*.txt|All files|*.*"
        extractedFile = wx.FileDialog (None, "Choose a file containing the test Questions", os.getcwd(), "", fileChoices, wx.OPEN)
        
        if extractedFile.ShowModal() == wx.ID_OK:
            selectedFileName = extractedFile.GetPath()
            self.selectedFileText.SetValue(selectedFileName)
            self.populateFields(selectedFileName)
            self.OnQuestionOrderSelect(event)

            self.save.Enable()
            self.run.Enable()
            self.orderuser.Enable()
        extractedFile.Destroy()

    def populateFields(self, filename):
        self.content.SetValue('')
        testFileName = open(filename)
        contents = testFileName.readlines()
        for line in contents:
            self.content.WriteText(str(line))

    #Selects the question number and populates it in a csv format on the textbox to assist
    #in the manual entry.
    def OnQuestionOrderSelect(self, event):
        orderingSerial = ''
        contents = self.content.GetValue()
        if len(contents) == 0:
            self.GiveError('Unable to load questions for counting')
            return
        results = self.SplitContentIntoQuestions(contents)
        self.orderField.SetValue('')
        self.orderField.SetValue(results[:-2])

    def SplitContentIntoQuestions(self, contents, provideQuestions = False):
        lines = contents.split('\n')
        self.extra_contents = []
        orderingSerial = ''
        questions = []
        question_content = ''
        qStarted = False
        # Delimit the questions on the basis of a common suffix after question number, the .
        # After the dot, there can be a single space or tab which separates the question number with the contents
        for cnt in range(0, len(lines)):
            line = lines[cnt]
            if line.__contains__('. ') or line.__contains__('.\t'):
                qStarted = True
                try:
                    qNumber = int(line.split('.')[0])
                    orderingSerial+= str(qNumber) + ', '
                    question_content = line#.split('.')[1]
                except UnicodeError as err:
                    orderingSerial+= 'X, '
                except ValueError as valErr:
                    None
            elif qStarted == False and line.strip() != '':
                orderingSerial+= '*, '
                self.extra_contents.append('\n'+line)
            elif line.startswith('(D)'):
                qStarted = False
                question_content+='\n'+line
                questions.append(question_content)
            else:
                if qStarted:
                    question_content += '\n'+line
                else:
                    None#self.extra_contents.append('\n'+line)
        
        if provideQuestions:
            return questions
        else:
            return orderingSerial
                
    #set the order of tests on the basis of specified test order
    def OnUseOrder(self, event):
        order = self.orderField.GetValue()
        if order == '':
            return
        questions = self.splitRawData(self.content.GetValue())
        order = order.split(',')
        details = dict()

        #Sort the questions according to the specified numbers, using a dictionary
        for ques in questions:
            details[ques[:ques.index('.')].strip()] = ques

        self.content.SetValue('')
        self.orderField.SetValue('')
        newcontent = ''
        for question in order:
            newcontent += str(details.pop(question.strip()) + self.splitDelim)
        newcontent = newcontent[:-len(self.splitDelim)]
        self.content.SetValue(newcontent)
        self.OnQuestionOrderSelect(event)

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