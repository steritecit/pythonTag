NotInheritable Class PLC_Comms


    ''' <summary>
    ''' Prevent instantiation by making new private
    ''' </summary>
    Private Sub New()

    End Sub
    Public Shared Sub WriteCycleFile(ByRef pLDS As LoaderDataStructure)

        'Load the specified file into the PLC.
        Dim strSub As String = "SendCycleFileToPLC"
        Dim PLC As Controller = New Controller()
        Dim LogixTag As Logix.Tag = Nothing
        Dim LogixGroup As Logix.TagGroup = Nothing
        Dim ErrorCode As Integer = 0

        Dim nDgvColMax As Integer = 0

        Dim nDgvRow As Integer = 0
        Dim nDgvRowMax As Integer = 0

        'Dim nPlcCol As Integer = 0
        'Dim nEmptyRowCount As Integer = 0

        Dim strPhase As String = String.Empty
        Dim strPlcTagRow As String = String.Empty
        Dim strPlcTag As String = String.Empty
        Dim nSubID As Integer = 0

        Dim strWork As String = String.Empty
        Dim strTest As String = "A"
        Dim nPlcRow As Integer = 0

        Dim colPhaseNames As Collection(Of String) = Nothing
        Dim colPhaseSubID As Collection(Of String) = Nothing
        Dim nPhaseNameIndex As Integer = 0
        Dim strSubID As String = String.Empty
        Dim nSubPhaseInjectMS As Integer = 0
        Dim nSubPhaseEvacMS As Integer = 0
        Dim EO_Cycle As Boolean = False
        Dim nPercentIncrement As Single = 0.0
        Dim nPercentComplete As Single = 0.0

        Dim dtStart As Date = Now
        Dim dtStop As Date = Nothing
        Dim tsDelta As TimeSpan = Nothing

        Try

            If pLDS.dgvCycle Is Nothing Then
                Main.UpdateLog("pDgv Is Nothing", strSub)
                Exit Try
            End If

            If pLDS.dgvCycle.RowCount = 0 Then Exit Try
            If pLDS.dgvCycle.ColumnCount < 20 Then Exit Try

            'Determine EO or ST from approved chamber cell
            strPhase = pLDS.dgvCycle.Rows(0).Cells(2).Value.ToString.Trim
            If strPhase.Equals("Approved Chambers") Then
                EO_Cycle = True
            ElseIf strPhase.Equals("Approved EO Chambers") Then
                EO_Cycle = True
            ElseIf strPhase.Equals("Approved Steam Chambers") Then
                EO_Cycle = False
            Else
                Exit Try
            End If


            'Load the phase name and subroutine ID collections
            'This will map each phase name to a unique subroutine id for the PLC.
            colPhaseSubID = PhaseNameData(0, EO_Cycle)
            colPhaseNames = PhaseNameData(1, EO_Cycle)

            'Set cells with nothing values to empty strings.
            Utilities.InitDgv_EmptyStrings(pLDS.dgvCycle)

            nDgvColMax = pLDS.dgvCycle.ColumnCount - 1
            nDgvRowMax = pLDS.dgvCycle.RowCount - 1
            'Calculate percent complete increment
            'One increment per row plus one for the signatures at the end.
            nPercentIncrement = 100 / (pLDS.dgvCycle.RowCount + 1)
            'UpdateLog(nDgvRowMax.ToString, "nDgvRowMax")

            PLC.IPAddress = pLDS.IpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            ErrorCode = PLC.Connect

            strTest = strTest & "D"

            If ErrorCode.Equals(0) Then
                If PLC.IsConnected Then

                    For nDgvRow = 0 To nDgvRowMax

                        strPhase = pLDS.dgvCycle.Rows(nDgvRow).Cells(2).Value.ToString.Trim
                        If strPhase.Contains("Approved") And strPhase.Contains("Chambers") Then Continue For

                        LogixGroup = New Logix.TagGroup

                        '***************************************************************************

                        'PLC row is one less than dgv row due to approved chambers line at the top of the dgv.
                        nPlcRow = nDgvRow - 1

                        strPlcTagRow = "SC_Phases[" & nPlcRow.ToString & "]"
                        '***************************************************************************
                        'Set the phase name
                        strPlcTag = strPlcTagRow & ".Name#40"

                        'Column 2 is for phase/sub id.
                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.STRING) With {.Value = strPhase}
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        'Phase Time
                        strPlcTag = strPlcTagRow & ".PhaseTimeMS"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.DINT) With {.Value = -1}

                        'Column 8 is for estimated time which is a string value HH:MM:SS
                        strWork = pLDS.dgvCycle.Rows(nDgvRow).Cells(8).Value.ToString.Trim

                        If strWork.Length.Equals(8) Then
                            LogixTag.Value = Utilities.ParseTimeStringMS(strWork)
                        End If

                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        nSubPhaseInjectMS = 0
                        nSubPhaseEvacMS = 0

                        GetSubPhaseTimes(strPhase, pLDS.dgvCycle.Rows(nDgvRow), nSubPhaseInjectMS, nSubPhaseEvacMS)

                        '***************************************************************************
                        'Sub Phase Time - Inject
                        strPlcTag = strPlcTagRow & ".SubPhaseInjectMS"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.DINT) With {.Value = nSubPhaseInjectMS}
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        'Sub Phase Time - Evac
                        strPlcTag = strPlcTagRow & ".SubPhaseEvacMS"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.DINT) With {.Value = nSubPhaseEvacMS}

                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        'Set the subroutine ID based upon the phase name lookup.
                        nPhaseNameIndex = colPhaseNames.IndexOf(strPhase)
                        strSubID = colPhaseSubID(nPhaseNameIndex)

                        strPlcTag = strPlcTagRow & ".SubID_File"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.INT) With {.Value = 0}

                        If Integer.TryParse(strSubID, nSubID) Then
                            If nSubID > 0 Then
                                LogixTag.Value = nSubID
                            End If
                        End If
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        'Column 10 is a flag for the Abort Start Point which is a boolean value.
                        strPlcTag = strPlcTagRow & ".AbortStartPoint"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.BOOL) With {.Value = False}

                        strWork = pLDS.dgvCycle.Rows(nDgvRow).Cells(10).Value.ToString.Trim
                        If strWork.Equals("ASP") Then
                            LogixTag.Value = True
                        End If
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        ' COLUMNS
                        WriteCycleFile_Columns(pLDS.dgvCycle.Rows(nDgvRow), strPlcTagRow, nDgvColMax, LogixGroup)
                        '***************************************************************************

                        'Increment Percent Complete
                        nPercentComplete = nPercentComplete + nPercentIncrement

                        strPlcTag = "SC.CycleLoader.PercentComplete"

                        LogixTag = New Tag(strPlcTag, Tag.ATOMIC.REAL) With {.Value = nPercentComplete}
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************

                        'Write a row of data
                        PLC.GroupWrite(LogixGroup)
                        Main.UpdateLog(PLC.ErrorCode.ToString & ":" & PLC.ErrorString, "GroupWrite:PLC.ErrorCode:Row:" & nDgvRow & " Tag Count:" & LogixGroup.Count.ToString)
                        LogixGroup = Nothing

                    Next 'Row

                    '************************************************************
                    ' END CYCLE PHASE DATA
                    '************************************************************
                    ' BEGIN CHECKSUM, USERNAME, SIGNATURES, HASH (CUSH)
                    '************************************************************

                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.CheckSum_File") With {
                        .DataType = Logix.Tag.ATOMIC.DINT,
                        .Value = pLDS.CheckSum
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************
                    'Loaded Cycle File
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.LoadedFileName") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = My.Computer.FileSystem.GetName(pLDS.FileName)
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************
                    'Loaded Cycle File User Name
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.UserName") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = pLDS.UserName
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************
                    'Loaded Cycle File Signatare 1
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.Signature1") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = pLDS.Signature1
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************
                    'Loaded Cycle File Signatare 2
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.Signature2") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = pLDS.Signature2
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************

                    'Clear error message since load was successfull
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.ErrorMessage") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = "OK"
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************

                    'Percent Complete
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.PercentComplete") With {
                        .DataType = Logix.Tag.ATOMIC.REAL,
                        .Value = 100.0
                    }
                    PLC.WriteTag(LogixTag)


                    '************************************************************
                    dtStop = Now
                    tsDelta = dtStop - dtStart

                    'LoadTimeMS
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.LoadTimeMS") With {
                        .DataType = Logix.Tag.ATOMIC.DINT,
                        .Value = tsDelta.Milliseconds
                    }
                    PLC.WriteTag(LogixTag)

                    '************************************************************

                    'Trigger checksum calculation
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.CycleLoader.CheckSum_Trigger") With {
                        .DataType = Logix.Tag.ATOMIC.BOOL,
                        .Value = True
                    }
                    PLC.WriteTag(LogixTag)

                    PLC.Disconnect()

                End If 'Connected
            Else
                Main.UpdateLog(ErrorCode.ToString, "PLC Connection Error Code")
            End If 'ErrorCode
            '************************************************************

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message & ":Row:" & nDgvRow.ToString, strSub & strTest)

        End Try

    End Sub

    Private Shared Sub GetSubPhaseTimes(ByVal pPhaseName As String, ByRef pDgvRow As DataGridViewRow, ByRef pInjectMS As Integer, ByRef pEvacMS As Integer)

        Try

            Select Case pPhaseName
                Case "Inert Dilution", "Gas Wash"
                    CFG_EO_Phase_Time.EO_PhaseTime(pDgvRow, True, pInjectMS, pEvacMS)

            End Select

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message, "GetSubPhaseTimes")
        End Try

    End Sub

    Public Shared Function ReadPlcMobileData(ByVal pIpAddress As String, ByVal pLength As Integer) As Logix.Tag

        'Read Mobile Data from the PLC.
        'This function is triggered by the PLC when the PLC sends the length of the message to be read.
        'The Mobile_SINT_Array is an array of SINT containing ASCII characters with the length specified by the PLC when the mobile data message is built.

        Dim strSub As String = "ReadPlcMobileData"

        Dim PLC As Controller = New Controller()
        Dim LogixTag As Logix.Tag = Nothing
        Dim LogixGroup As Logix.TagGroup = Nothing
        Dim ErrorCode As Integer = 0
        Dim strTest As String = "A"

        Try

            PLC.IPAddress = pIpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            ErrorCode = PLC.Connect

            If ErrorCode.Equals(0) Then
                If PLC.IsConnected Then

                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("Mobile_SINT_Array[0]") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Length = pLength
                    }

                    PLC.ReadTag(LogixTag)

                    If PLC.ErrorCode = 0 Then
                        'Do nothing
                    Else
                        Main.UpdateLog(PLC.ErrorString, strSub)
                    End If

                    PLC.Disconnect()

                End If
            End If

        Catch ex As Exception

            Main.UpdateSqlLog(ex.Message, strSub & strTest)

        End Try

        Return LogixTag

    End Function

    Private Shared Sub WriteCycleFile_Columns(ByRef pDgvRow As DataGridViewRow, ByVal pPlcTagRow As String, ByVal pDgvColMax As Integer, ByRef pTagGroup As Logix.TagGroup)

        'Called from LoadCycleFile
        'Part of sending data to the PLC

        Dim LogixTag As Logix.Tag = Nothing
        Dim nDgvCol As Integer = 0
        Dim nPlcCol As Integer = 0
        Dim strWork As String = String.Empty
        Dim strPhase As String = String.Empty
        Dim strPlcTag As String = String.Empty
        '*******************************
        Dim nDgvColStart As Integer = 12
        '*******************************

        Try

            For nDgvCol = nDgvColStart To pDgvColMax

                'MessageBox.Show(dgv.Rows(nDgvRow).Cells(nDgvCol).Value.ToString.Trim, nDgvRow.ToString & ":" & nDgvCol.ToString)

                strPhase = pDgvRow.Cells(2).Value.ToString.Trim

                'EVEN columns only !!!!!!!
                If (nDgvCol Mod 2).Equals(0) Then
                    'SC_Phases[0].P[0]
                    'Tag name includes #10 for string length
                    strPlcTag = pPlcTagRow & ".P[" & nPlcCol.ToString & "]#10"

                    'UpdateLog(strPlcTagCol, nPlcRow.ToString)

                    LogixTag = Nothing
                    LogixTag = New Logix.Tag(strPlcTag) With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = ""
                    }
                    '*******************************

                    strWork = pDgvRow.Cells(nDgvCol).Value.ToString.Trim
                    'UpdateLog("strWork:Row:" & nDgvRow.ToString & ":Col:" & nDgvCol.ToString & ":" & strWork, "")
                    'Look up the value in case it is from a list box.
                    'List box values are used for pressure and temperature units,
                    'sterilant selection, etc.
                    'strWork = Steritec.ListBoxTranslator(strPhase, nDgvCol - 10, strWork)

                    If strWork = "False" Then strWork = ""
                    If strWork.Length > 10 Then
                        LogixTag.Value = strWork.Substring(0, 10)
                    ElseIf strWork.Length > 0 Then
                        LogixTag.Value = strWork
                    End If

                    'UpdateLog("Value:" & LogixTag.Value.ToString, LogixTag.Name)

                    pTagGroup.AddTag(LogixTag)

                    nPlcCol = nPlcCol + 1

                    If nPlcCol < 20 Then
                        'Stay in column loop
                    Else
                        'UpdateLog("DGV has more data columns than PLC array", LogixTag.Name)
                        Exit For
                    End If

                End If 'Even columns only

            Next 'Column

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message, "LoadCycleFileColumns")
        End Try

    End Sub


    Public Shared Sub WriteCalData(ByRef pCalData() As PLC_UDT_Analog_CAL, ByVal pIpAddress As String)

        'Load the specified calibration data to the PLC.
        Dim strSub As String = "WriteCalData"
        Dim PLC As Controller = New Controller()
        Dim LogixTag As Logix.Tag = Nothing
        Dim LogixGroup As Logix.TagGroup = Nothing
        Dim ErrorCode As Integer = 0

        Dim nRow As Integer = 0
        Dim nRowMax As Integer = 0

        Dim strPlcTag As String = String.Empty

        Dim strWork As String = String.Empty
        Dim strTest As String = "A"

        Dim dtStart As Date = Now
        Dim dtStop As Date = Nothing
        Dim tsDelta As TimeSpan

        Try

            If pCalData Is Nothing Then
                Main.UpdateLog(pIpAddress & " : " & "pCalData Is Nothing", "SendCalDataToPLC")
                Exit Try
            End If

            nRowMax = pCalData.GetUpperBound(0)

            PLC.IPAddress = pIpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            ErrorCode = PLC.Connect

            strTest = strTest & "B"

            If ErrorCode.Equals(0) Then
                If PLC.IsConnected Then

                    For nRow = 0 To nRowMax

                        LogixGroup = New Logix.TagGroup

                        '***************************************************************************
                        'Build the tag name
                        strPlcTag = "AA_Analog[" & pCalData(nRow).Index.ToString.Trim & "].CAL."

                        'UpdateLog(strPlcTag, "SendCalDataToPLC:strPlcTag")

                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Tag#20")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.STRING
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).Tag.Trim
                        LogixGroup.AddTag(LogixTag)

                        '***************************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "EngUnits#10")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.STRING
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).EngUnits.Trim
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Description#40")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.STRING
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).Description.Trim
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "RawMin")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.REAL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).RawMin
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "RawMax")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.REAL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).RawMax
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "EUMin")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.REAL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).EUMin
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "EUMax")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.REAL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).EUMax
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Index")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.INT
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).Index
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Loaded")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.BOOL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).Loaded
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Signed")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.BOOL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).Signed
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        'Mobile_Enable
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Mobile_Enable")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.BOOL
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).mobile_enable
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        'Mobile_Label
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Mobile_Label#40")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.STRING
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).mobile_label.Trim
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        'Mobile_Location
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Mobile_Location#20")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.STRING
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).mobile_location
                        LogixGroup.AddTag(LogixTag)
                        '************************************************************
                        'Mobile_Priority
                        LogixTag = Nothing
                        LogixTag = New Logix.Tag(strPlcTag & "Mobile_Priority")
                        strTest = strTest & "C"
                        LogixTag.DataType = Logix.Tag.ATOMIC.INT
                        strTest = strTest & "D"
                        LogixTag.Value = pCalData(nRow).mobile_priority
                        LogixGroup.AddTag(LogixTag)

                        '************************************************************
                        'Write one index of cal data

                        strTest = strTest & "F" & PLC.GroupWrite(LogixGroup).ToString
                        Main.UpdateLog(pIpAddress & " : " & PLC.ErrorCode.ToString & ":" & PLC.ErrorString, "GroupWrite:PLC.ErrorCode:Row:" & nRow & " Tag Count:" & LogixGroup.Count.ToString)
                        LogixGroup = Nothing

                    Next 'Row

                    strTest = strTest & "E"

                    '************************************************************

                    strTest = strTest & "G"

                    PLC.Disconnect()

                End If 'Connected
            Else
                Main.UpdateLog(ErrorCode.ToString, strSub & ":PLC Connection Error Code")
            End If 'ErrorCode
            '************************************************************

            dtStop = Now
            tsDelta = dtStop - dtStart

            'Send the elapsed time to the database log.
            Main.UpdateSqlLog("Time: " & tsDelta.ToString, strSub)

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message & ":Row:" & nRow.ToString, strSub & ":" & strTest)

        End Try

    End Sub

    Public Shared Sub WriteTrendTimeSpan(ByVal pIndex As Integer)

        'Load the specified file into the PLC.

        Dim strSub As String = "WriteTrendTimeSpan"
        Dim PLC As Controller = New Controller()
        Dim LogixTag As Logix.Tag = Nothing
        Dim LogixGroup As Logix.TagGroup = Nothing
        Dim ErrorCode As Integer = 0

        Dim nTimeSpanMin As Integer = 0

        Try

            PLC.IPAddress = SteritecGlobals.Data(pIndex).IpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            ErrorCode = PLC.Connect

            If ErrorCode.Equals(0) Then
                If PLC.IsConnected Then

                    '************************************************************
                    nTimeSpanMin = SteritecGlobals.Data(pIndex).TrendData.TrendTimeSpanMIN
                    'Round to nearest 10 minutes to minimize changes to trend.
                    nTimeSpanMin = CType(Math.Ceiling(nTimeSpanMin / 10) * 10, Integer)
                    '************************************************************

                    'Loaded Cycle File
                    LogixTag = Nothing
                    LogixTag = New Logix.Tag("SC.Press.TrendTimeSpanMIN") With {
                        .DataType = Logix.Tag.ATOMIC.INT,
                        .Value = nTimeSpanMin
                    }
                    PLC.WriteTag(LogixTag)

                    PLC.Disconnect()

                End If 'Connected
            Else
                Main.UpdateLog(ErrorCode.ToString, "PLC Connection Error Code")
            End If 'ErrorCode
            '************************************************************

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message, strSub)

        End Try

    End Sub


    Public Shared Sub WriteErrorMessage(ByVal pIpAddress As String, ByVal pError As String)

        'This writes the error message related to the loading of a cycle.

        Dim strSub As String = "WriteErrorMessage"
        Dim PLC As Controller = New Controller()
        Dim LogixTag As Logix.Tag = Nothing

        Dim nErrorCode As Integer = 0
        Try

            PLC.IPAddress = pIpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            nErrorCode = PLC.Connect

            If nErrorCode.Equals(0) Then
                If PLC.IsConnected Then
                    LogixTag = New Logix.Tag("SC.CycleLoader.ErrorMessage") With {
                        .DataType = Logix.Tag.ATOMIC.STRING,
                        .Value = pError
                    }
                    PLC.WriteTag(LogixTag)
                    PLC.Disconnect()
                End If
            Else
                Main.UpdateLog(pIpAddress & " : If nErrorCode.Equals(0) Then : " & PLC.ErrorString, "SendErrorMessageToPLC")
            End If

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message & " : " & pError, strSub)
        End Try

    End Sub

    Private Shared Function PhaseNameData(ByVal pCol As Integer, ByVal pEO_Cycle As Boolean) As Collection(Of String)

        'Use the column number to get a collection of all the data in that column.

        Dim nMax As Integer = 0
        Dim n As Integer = 0
        Dim colReturn As Collection(Of String) = New Collection(Of String)
        Try

            If pCol < 0 Then Exit Try
            If pCol > 1 Then Exit Try

            If pEO_Cycle Then

                'EO EO EO EO EO EO
                nMax = Steritec.EO_PhaseNames.GetUpperBound(0)

                For n = 0 To nMax
                    colReturn.Add(Steritec.EO_PhaseNames(n, pCol))
                Next
            Else
                'ST ST ST ST ST ST ST ST
                nMax = Steritec.ST_PhaseNames.GetUpperBound(0)

                For n = 0 To nMax
                    colReturn.Add(Steritec.ST_PhaseNames(n, pCol))
                Next
            End If

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message, "PhaseNameToSubID")
        End Try

        Return colReturn

    End Function


    Public Shared Function ReadString(ByVal pIpAddress As String, ByVal pTagName As String) As String

        Dim strSub As String = "ReadString"
        Dim PLC As Logix.Controller = New Logix.Controller
        Dim LogixTag As Logix.Tag = Nothing
        Dim ErrorCode As Integer = 0
        Dim strReturnVal As String = String.Empty

        Try

            If pTagName.Length.Equals(0) Then
                Main.UpdateLog(pIpAddress & " : pTagName : length equals zero", strSub)
            Else
                Main.UpdateLog(pIpAddress & " : pTagName:" & pTagName, strSub)
            End If

            PLC.IPAddress = pIpAddress
            PLC.CPUType = Controller.CPU.LOGIX

            ErrorCode = PLC.Connect

            If ErrorCode.Equals(0) Then

                LogixTag = New Logix.Tag(pTagName, Logix.Tag.ATOMIC.STRING)

                PLC.ReadTag(LogixTag)

                If LogixTag.ErrorCode.Equals(0) Then
                    If Not LogixTag.Value Is Nothing Then
                        strReturnVal = LogixTag.Value.ToString.Trim
                        Main.UpdateLog(pIpAddress & " : LogixTag.Name : " & LogixTag.Name & " : " & strReturnVal, strSub)
                    End If
                Else
                    Main.UpdateLog(pIpAddress & " : " & pTagName & ":" & LogixTag.ErrorString, strSub)
                End If

            End If

        Catch ex As Exception
            Main.UpdateSqlLog(ex.Message, strSub)
        End Try

        Return strReturnVal

    End Function

End Class
