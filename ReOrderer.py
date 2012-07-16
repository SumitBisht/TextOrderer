import wx
import os
import random
'''
This is the main class that provides the UI and logic for the text block randomization.
'''
class ReOrderer(wx.Frame):

    def __init__(self):
        self.splitDelim = '\n\n'
    	wx.Frame.__init__(self, None, -1, 'Question Randomizer', size=(600, 400))
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        menubar = wx.MenuBar()
        menu = wx.Menu()
        menu.Append(101, "&Open", "Open a text file containing tests")
        self.Bind(wx.EVT_MENU, self.OnFileSelect, id=101)
        menubar.Append(menu, "&File")
        menu = wx.Menu()
        menu.Append(201, "&Set Order", "Set the default ordering of tests")
        self.Bind(wx.EVT_MENU, self.OnQuestionOrderSelect, id=201)
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
        self.save.Disable()
        self.run.Disable()
        
        buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonsizer.Add(self.save, 1, wx.EXPAND)
        buttonsizer.Add(self.run, 2, wx.EXPAND)
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
        if len(paperContent) == 0:
            self.GiveError('Nothing to randomize')
            return
        splits = paperContent.split(self.splitDelim)
        print "splitted contents are:"
        for i in Range(0, len(splits)):
            splits[i] = splits[i].strip(self.splitDelim)
        random.shuffle(splits)
        newContent = ""
        self.content.SetValue("")
        for item in splits:
            newContent += item
            newContent += self.splitDelim
        self.content.SetValue(newContent.rstrip(self.splitDelim))

    def OnFileSelect(self, event):
        fileChoices = "Text file |*.txt|All files|*.*"
        extractedFile = wx.FileDialog (None, "Choose a file containing the test Questions", os.getcwd(), "", fileChoices, wx.OPEN)
        
        if extractedFile.ShowModal() == wx.ID_OK:
            selectedFileName = extractedFile.GetPath()
            self.selectedFileText.SetValue(selectedFileName)
            self.populateFields(selectedFileName)

            self.save.Enable()
            self.run.Enable()
        extractedFile.Destroy()

    def populateFields(self, filename):
        testFileName = open(filename)
        contents = testFileName.readlines()
        for line in contents:
            self.content.WriteText(str(line))

    def OnQuestionOrderSelect(self, event):
        orderingSerial = ''
        content = self.content.GetValue()
        if len(content) == 0:
            self.GiveError('Unable to load questions for counting')
            return
        questionCount = len(content.split(self.splitDelim))
        for cnt in range(0, questionCount):
            orderingSerial+=str(cnt)+', '
        self.orderField.SetValue("")
        self.orderField.SetValue(orderingSerial[:-2])

    # Provides error dialogs in a resuable manner.
    # Is based on the presence of loaded file contents
    def GiveError(self, actionPerformed):
        dlg=wx.MessageDialog(self, 'Please load text file containing Questions', actionPerformed, wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
        dlg.ShowModal()
        dlg.CenterOnScreen()
        dlg.Destroy()

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