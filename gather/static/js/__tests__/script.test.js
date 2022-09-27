/**
 * @jest-environment jsdom
 */

const turnArrayIntoString = require("../script");

beforeAll(() => {
    document.body.innerHTML = "<div id='div' class='array-string'>['a', 'b', 'c']</div>";
});

describe("DOM tests", () => {
    test("expects array content to turn into string", () => {
        turnArrayIntoString();
        expect(document.getElementById("div").innerHTML).toEqual("a, b, c");
    });
});