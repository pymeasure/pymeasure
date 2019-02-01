import win32com.client #imports the pywin32 library

scope=win32com.client.Dispatch("LeCroy.ActiveDSOCtrl.1")  #creates instance of the ActiveDSO control
scope.MakeConnection("IP:146.136.35.208") #Connects to the oscilloscope.  Substitute your IP address

scope.WriteString("*IDN?",1)
print(scope.ReadString(1000))
# scope.WriteString("C1:VDIV 0.1",1) #Remote Command to set C1 volt/div setting to 20 mV.
scope.WriteString("VBS? 'return=app.Measure.P7.Out.Result.Value' ",1)
print(scope.ReadString(80))

scope.Disconnect() #Disconnects from the oscilloscope

