function validateDate(dateStr) {
  // 1. Check if it has exactly one '/'
  if ((dateStr.match(/\//g) || []).length !== 1) {
    return false;
  }

  // 2. Split the string and check if we have exactly 2 parts
  const parts = dateStr.split('/');
  if (parts.length !== 2) {
    return false;
  }

  const [monthStr, dayStr] = parts;

  // 3. Check if both parts have exactly 2 digits
  if (monthStr.length !== 2 || dayStr.length !== 2) {
    return false;
  }

  // 4. Check that all characters are digits using charCodeAt
  for (let i = 0; i < 2; i++) {
    const monthChar = monthStr.charCodeAt(i);
    const dayChar = dayStr.charCodeAt(i);
    if (
      monthChar < 48 || monthChar > 57 ||
      dayChar < 48 || dayChar > 57
    ) {
      return false;
    }
  }

  // 5. Convert parts to numbers
  const monthNum = parseInt(monthStr, 10);
  const dayNum = parseInt(dayStr, 10);

  // 6. Check if month is between 1 and 12
  if (monthNum < 1 || monthNum > 12) {
    return false;
  }

  // 7. Check if day is valid for the given month
  const daysInMonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
  const maxDay = daysInMonth[monthNum - 1];

  if (dayNum < 1 || dayNum > maxDay) {
    return false;
  }

  // 8. Return true if all checks pass
  return true;
}

function calculatePriority(dateStr, timeStr) {
  // Split date and time strings
  const dateParts = dateStr.split('/');
  const timeParts = timeStr.split(':');
  // Convert to numbers
  const month = parseInt(dateParts[0], 10); 
  const day = parseInt(dateParts[1], 10);
  const hours = parseInt(timeParts[0], 10);
  const minutes = parseInt(timeParts[1], 10);
  const currentYear = new Date().getFullYear();
  const dueDate = new Date(currentYear, month - 1, day, hours, minutes);
  // Get current year
  // Get current date
  // write the code to get the year
  
  // Parse the date and time
  // write the code to parse the date and time
  
  // Create a date object for the due date
  // write the code to create a date object for the due date
  
  // For sorting, we'll use a more precise priority based on exact timestamp
  // Return the timestamp itself for more accurate sorting
  return dueDate.getTime();
}

function validateTime(timeStr) {
  const parts = timeStr.split(':');
  if (parts.length !== 2) return false;

  const [hoursStr, minutesStr] = parts;
  if (hoursStr.length !== 2 || minutesStr.length !== 2) return false;

  const hours = parseInt(hoursStr, 10);
  const minutes = parseInt(minutesStr, 10);

  return (
    !isNaN(hours) &&
    !isNaN(minutes) &&
    hours >= 0 && hours <= 23 &&
    minutes >= 0 && minutes <= 59
  );
}

module.exports = { validateDate, validateTime, calculatePriority };
