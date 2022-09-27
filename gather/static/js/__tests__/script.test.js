
const addition = require("../script");
const turnArrayIntoString = require("../script");

describe("Recipe Formatting", () => {
    describe("Turn array into string", () => {
        test("should return a string seperated by commas from a provided array", () =>{
            expect(turnArrayIntoString(['a', 'b', 'c'])).toBe("a, b, c");
        })

    });
});

describe("Calculator", () => {
    describe("Addition function", () => {
        test("shouuld return 42 for 20 + 22", () => {
            expect(addition(20, 22)).toBe(42);
        });
    });
});

