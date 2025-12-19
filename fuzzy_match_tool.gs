function findMismatchingTitles() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const trainSheet = ss.getSheetByName("Training Data");
  const testSheet = ss.getSheetByName("Testing Data");
  const outputSheet = ss.getSheetByName("Potential Matches") || ss.insertSheet("Potential Matches");

  const trainTitles = trainSheet.getRange(2, 1, trainSheet.getLastRow() - 1, 1).getValues().flat();
  const testTitles = testSheet.getRange(2, 1, testSheet.getLastRow() - 1, 1).getValues().flat();

  const missingTitles = testTitles.filter(t => !trainTitles.includes(t));

  const apiKey = PropertiesService.getScriptProperties().getProperty("GEMINI_API_KEY");
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key=${apiKey}`;

  const prompt = `
    I have two lists of movies.
    List A (Valid Database Names): ${JSON.stringify(trainTitles)}
    List B (Unmatched Names): ${JSON.stringify(missingTitles)}

    Task: Identify movies in List B that are actually the same as movies in List A but written differently (e.g. typos, "Se7en" vs "Seven", "Part 2" vs "II").
    
    Return ONLY a JSON object with the matches like this: {"Bad Name": "Correct Name From List A"}.
    If no match is found for a title, ignore it.
  `;

  const payload = {
    "contents": [{
      "parts": [{ "text": prompt }]
    }]
  };

  const options = {
    "method": "post",
    "contentType": "application/json",
    "payload": JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    const data = JSON.parse(response.getContentText());
    const resultText = data.candidates[0].content.parts[0].text;
    
    const matches = JSON.parse(resultText);

    outputSheet.clear();
    outputSheet.appendRow(["Testing Data Title (Bad)", "Training Data Title (Good)", "Status"]);
    
    for (const [bad, good] of Object.entries(matches)) {
      outputSheet.appendRow([bad, good, "Pending Verification"]);
    }
    
    Logger.log("Check the 'Potential Matches' sheet for review.");

  } catch (e) {
    Logger.log("Error: " + e.toString());
  }
}
