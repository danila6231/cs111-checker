// Test suite for Project 2
const assert = require('assert');

// Import student's code
let studentCode = '';
try {
    studentCode = require('./student_solution.js');
} catch (e) {
    console.error('Error loading student solution:', e.message);
    process.exit(1);
}

const { validateDate, validateTime, calculatePriority } = studentCode;

// Test cases for validateDate
describe('validateDate', () => {
    // Valid dates
    it('should accept valid dates', () => {
        assert.strictEqual(validateDate('01/01'), true);
        assert.strictEqual(validateDate('12/31'), true);
        assert.strictEqual(validateDate('02/28'), true);
        assert.strictEqual(validateDate('04/30'), true);
    });

    // Invalid format
    it('should reject strings without exactly one forward slash', () => {
        assert.strictEqual(validateDate('0101'), false);
        assert.strictEqual(validateDate('01//01'), false);
        assert.strictEqual(validateDate('01/01/'), false);
    });

    // Invalid digit count
    it('should reject parts that are not exactly 2 digits', () => {
        assert.strictEqual(validateDate('1/01'), false);
        assert.strictEqual(validateDate('01/1'), false);
        assert.strictEqual(validateDate('001/01'), false);
        assert.strictEqual(validateDate('01/001'), false);
    });

    // Non-numeric characters
    it('should reject non-numeric characters', () => {
        assert.strictEqual(validateDate('0a/01'), false);
        assert.strictEqual(validateDate('01/0b'), false);
        assert.strictEqual(validateDate('ab/cd'), false);
    });

    // Invalid months
    it('should reject invalid months', () => {
        assert.strictEqual(validateDate('00/01'), false);
        assert.strictEqual(validateDate('13/01'), false);
        assert.strictEqual(validateDate('99/01'), false);
    });

    // Invalid days for specific months
    it('should reject invalid days for each month', () => {
        // February
        assert.strictEqual(validateDate('02/30'), false);
        // 30-day months
        assert.strictEqual(validateDate('04/31'), false);
        assert.strictEqual(validateDate('06/31'), false);
        assert.strictEqual(validateDate('09/31'), false);
        assert.strictEqual(validateDate('11/31'), false);
        // All months
        assert.strictEqual(validateDate('01/32'), false);
        assert.strictEqual(validateDate('03/32'), false);
        assert.strictEqual(validateDate('05/32'), false);
    });
});

// Test cases for validateTime
describe('validateTime', () => {
    // Valid times
    it('should accept valid times', () => {
        assert.strictEqual(validateTime('00:00'), true);
        assert.strictEqual(validateTime('12:00'), true);
        assert.strictEqual(validateTime('23:59'), true);
    });

    // Invalid format
    it('should reject strings without exactly one colon', () => {
        assert.strictEqual(validateTime('0000'), false);
        assert.strictEqual(validateTime('00::00'), false);
        assert.strictEqual(validateTime('00:00:'), false);
    });

    // Invalid digit count
    it('should reject parts that are not exactly 2 digits', () => {
        assert.strictEqual(validateTime('0:00'), false);
        assert.strictEqual(validateTime('00:0'), false);
        assert.strictEqual(validateTime('000:00'), false);
        assert.strictEqual(validateTime('00:000'), false);
    });

    // Non-numeric characters
    it('should reject non-numeric characters', () => {
        assert.strictEqual(validateTime('0a:00'), false);
        assert.strictEqual(validateTime('00:0b'), false);
        assert.strictEqual(validateTime('ab:cd'), false);
    });

    // Invalid hours
    it('should reject invalid hours', () => {
        assert.strictEqual(validateTime('24:00'), false);
        assert.strictEqual(validateTime('25:00'), false);
        assert.strictEqual(validateTime('99:00'), false);
    });

    // Invalid minutes
    it('should reject invalid minutes', () => {
        assert.strictEqual(validateTime('00:60'), false);
        assert.strictEqual(validateTime('00:99'), false);
    });
});

// Test cases for calculatePriority
describe('calculatePriority', () => {
    // Mock current date for consistent testing
    let originalDate;
    beforeEach(() => {
        originalDate = global.Date;
        const mockDate = new Date(2024, 0, 1); // January 1, 2024
        global.Date = class extends Date {
            constructor(...args) {
                if (args.length === 0) {
                    return mockDate;
                }
                return new originalDate(...args);
            }
        };
        global.Date.now = () => mockDate.getTime();
    });

    afterEach(() => {
        global.Date = originalDate;
    });

    // Valid inputs
    it('should correctly calculate timestamp for valid inputs', () => {
        // Test with various dates and times
        assert.strictEqual(
            calculatePriority('01/01', '09:00'),
            new Date(2024, 0, 1, 9, 0).getTime()
        ); // Jan 1, 2024, 09:00
        assert.strictEqual(
            calculatePriority('01/01', '17:00'),
            new Date(2024, 0, 1, 17, 0).getTime()
        ); // Jan 1, 2024, 17:00
        assert.strictEqual(
            calculatePriority('01/02', '09:00'),
            new Date(2024, 0, 2, 9, 0).getTime()
        ); // Jan 2, 2024, 09:00
        assert.strictEqual(
            calculatePriority('01/02', '17:00'),
            new Date(2024, 0, 2, 17, 0).getTime()
        ); // Jan 2, 2024, 17:00
        assert.strictEqual(
            calculatePriority('01/15', '09:00'),
            new Date(2024, 0, 15, 9, 0).getTime()
        ); // Jan 15, 2024, 09:00
    });

    // Edge cases
    it('should handle edge cases correctly', () => {
        assert.strictEqual(
            calculatePriority('12/31', '23:59'),
            new Date(2024, 11, 31, 23, 59).getTime()
        ); // Dec 31, 2024, 23:59
        assert.strictEqual(
            calculatePriority('01/01', '00:00'),
            new Date(2024, 0, 1, 0, 0).getTime()
        ); // Jan 1, 2024, 00:00
        assert.strictEqual(
            calculatePriority('01/01', '23:59'),
            new Date(2024, 0, 1, 23, 59).getTime()
        ); // Jan 1, 2024, 23:59
    });
}); 