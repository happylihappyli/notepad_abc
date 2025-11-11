
Set oShell = CreateObject("WScript.Shell")
sDesktop = oShell.SpecialFolders("Desktop")
Set oLink = oShell.CreateShortcut("E:\GitHub3\notepad_abc\bin\notepad_abc_compatible.lnk")
oLink.TargetPath = "E:\GitHub3\notepad_abc\bin\notepad_abc.exe"
oLink.WindowStyle = 1
oLink.HotKey = ""
oLink.IconLocation = "E:\GitHub3\notepad_abc\bin\notepad_abc.exe, 0"
oLink.Description = "Notepad ABC (Windows 7 Compatible)"
oLink.WorkingDirectory = "E:\GitHub3\notepad_abc\bin"
oLink.Save

' 设置兼容模式
Set oFSO = CreateObject("Scripting.FileSystemObject")
Set oApp = CreateObject("Shell.Application")

' 获取快捷方式
Set oFolder = oApp.NameSpace(oFSO.GetParentFolderName("E:\GitHub3\notepad_abc\bin\notepad_abc_compatible.lnk"))
Set oFile = oFolder.ParseName(oFSO.GetFileName("E:\GitHub3\notepad_abc\bin\notepad_abc_compatible.lnk"))

' 设置兼容模式
Set oVerb = Nothing
For Each Verb In oFile.Verbs
    If LCase(Verb.Name) = "兼容性疑难解答" Then
        Set oVerb = Verb
        Exit For
    End If
Next

If Not oVerb Is Nothing Then
    oVerb.DoIt
    WScript.Echo "已打开兼容性设置对话框，请手动设置Windows 7兼容模式"
Else
    WScript.Echo "无法找到兼容性设置选项"
End If
