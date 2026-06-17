/**
 * Go Kilimanjaro Treks — lead logger.
 * Receives a POST from the contact form and the packing-list popup and
 * appends one row per lead to the bound Google Sheet.
 *
 * ── ONE-TIME SETUP (Clinton / Nelson) ─────────────────────────────────────
 * 1. Create a Google Sheet (e.g. "Go Kilimanjaro Treks — Leads").
 * 2. Extensions → Apps Script. Delete the sample code, paste this whole file.
 * 3. Click Deploy → New deployment → type "Web app".
 *      - Description: "GKT lead logger"
 *      - Execute as: Me
 *      - Who has access: Anyone
 *    Deploy, authorise when prompted, and COPY the Web app URL
 *    (it ends in /exec).
 * 4. Paste that URL into src/data/site.ts → SITE.sheetEndpoint, commit/push.
 *    (Or send Clinton the URL to paste.) Leads then append automatically;
 *    email via FormSubmit keeps working unchanged.
 * 5. To test: submit the live contact form once and confirm a row appears.
 * ───────────────────────────────────────────────────────────────────────────
 */
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Leads')
             || SpreadsheetApp.getActiveSpreadsheet().insertSheet('Leads');

    // Header row, created once.
    var headers = ['Timestamp', 'Source', 'Name', 'Email', 'Phone', 'Country',
                   'Trip Type', 'Dates', 'Group Size', 'Fitness', 'Message'];
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(headers);
      sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
      sheet.setFrozenRows(1);
    }

    var p = (e && e.parameter) ? e.parameter : {};
    var source = p.source || (p._subject && /popup/i.test(p._subject) ? 'home-popup' : 'contact-form');
    sheet.appendRow([
      new Date(), source, p.name || '', p.email || '', p.phone || '', p.country || '',
      p.trip_type || '', p.dates || '', p.group_size || '', p.fitness || '', p.message || ''
    ]);

    return ContentService.createTextOutput(
      JSON.stringify({ result: 'ok' })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(
      JSON.stringify({ result: 'error', error: String(err) })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
