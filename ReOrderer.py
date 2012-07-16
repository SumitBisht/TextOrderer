import wx
import os
import random

class ReOrderer(wx.Frame):
    def __init__(self):
    	wx.Frame.__init__(self, None, -1, 'Question Randomizer', size=(600, 400))
        mainsizer = wx.BoxSizer(wx.VERTICAL)
        
        self.myStatusBar = wx.StatusBar(id=wx.NewId(), name='myStatusBar', parent=self, style=wx.ST_SIZEGRIP)
        self.statusLabel = wx.StaticText(self.myStatusBar,-1,'',(5, 3))
        self.statusLabel.ForegroundColour = 'Red'
        swiss_font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False)
        self.statusLabel.SetFont(swiss_font)
        
        self.selectedFileText = wx.TextCtrl(self, -1, "No File Selected", size=(500,25), style = wx.TE_READONLY)
        self.FileSelector = wx.Button(self, wx.NewId(), "Select File")
        self.Bind(wx.EVT_BUTTON, self.OnFileSelect, self.FileSelector)
        childsizer = wx.BoxSizer(wx.HORIZONTAL)
        childsizer.Add(self.selectedFileText, 1, wx.EXPAND)
        childsizer.Add(self.FileSelector, 0 , wx.EXPAND|wx.ALIGN_LEFT)
        mainsizer.Add(childsizer)

        self.content = wx.TextCtrl(self, style=wx.NO_BORDER|wx.TE_MULTILINE, size=(600,400));
        mainsizer.Add(self.content)
        
        self.save = wx.Button(self, -1, "Save Test")
        self.Bind(wx.EVT_BUTTON, self.OnSaveToFile, self.save)
        self.run = wx.Button(self, -1, "Randomize")
        self.Bind(wx.EVT_BUTTON, self.OnRandomize, self.run)
        
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
        splitDelim = '\n\n'
        paperContent = self.content.GetValue()
        if len(paperContent) == 0:
            dlg=wx.MessageDialog(self, 'Please load text file containing Questions', 'Nothing to Randomize', wx.OK | wx.ICON_INFORMATION | wx.STAY_ON_TOP)
            dlg.ShowModal()
            dlg.CenterOnScreen()
            dlg.Destroy()
            return
        splits = paperContent.split(splitDelim)
        print "splitted contents are:"
        for s in splits:
            print "\n-"+s+"-"
        random.shuffle(splits)
        newContent = ""
        self.content.SetValue("")
        for item in splits:
            newContent += item
            newContent += splitDelim
        self.content.SetValue(newContent.rstrip(splitDelim))

    def OnFileSelect(self, event):
        fileChoices = "Text file |*.txt|All files|*.*"
        extractedFile = wx.FileDialog (None, "Choose a file containing the test Questions", os.getcwd(), "", fileChoices, wx.OPEN)
        
        if extractedFile.ShowModal() == wx.ID_OK:
            selectedFileName = extractedFile.GetPath()
            self.selectedFileText.SetValue(selectedFileName)
            self.populateFields(selectedFileName)
        
        extractedFile.Destroy()

    def populateFields(self, filename):
        testFileName = open(filename)
        contents = testFileName.readlines()
        for line in contents:
            self.content.WriteText(str(line))


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