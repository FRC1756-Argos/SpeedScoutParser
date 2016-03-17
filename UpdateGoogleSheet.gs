function addDataRow(rowData) {
  if(rowData.length == 0)
  {
    return;
  }
  return rowData;
  files = DriveApp.getFilesByName(
     '2016 CIR Scouting');
  while (files.hasNext())
  {
    var spreadsheet = SpreadsheetApp.open(files.next());
    var sheet = spreadsheet.getSheetByName("Data");
    if(sheet == null)
    {
      return;
    }
    sheet.appendRow(rowData.value);
  }
}
