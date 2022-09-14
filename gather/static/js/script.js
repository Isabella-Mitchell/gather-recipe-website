 function setRecipeColourImage() {
    let colourCodes = document.getElementsByClassName("colour-code");
    let parent
    let colourCode
    for(let i = 0; i < colourCodes.length; i++) {
        parent = colourCodes[i].parentNode;
        colourCode = colourCodes[i].textContent;
        parent.style.backgroundColor = colourCode;
    }
};

// Reformate to include following function with if else statement
function turnArrayIntoString() {
    let arrayContainers = document.getElementsByClassName("array-string");
    let array;
    let removeBrackets;
    let string;
    for(let i = 0; i < arrayContainers.length; i++) {
        array = arrayContainers[i].textContent;  
        removeBrackets = array.replace(/\[|\]/g, '');
        string = removeBrackets.replace(/['"]+/g, '')
        console.log(string);
        arrayContainers[i].textContent = string
    }
};

// Reformate to include following function with if else statement
function turnStepsArrayIntoString() {
    let arrayContainers = document.getElementsByClassName("array-steps-string");
    let array;
    let removeBrackets;
    let replaceCommas;
    let removeColons;
    let string;
    for(let i = 0; i < arrayContainers.length; i++) {
        array = arrayContainers[i].textContent;  
        removeBrackets = array.replace(/\[|\]/g, '');
        string = removeBrackets.replace(/['"]+/g, ';');
        replaceCommas = string.replaceAll(";, ;", '\r\n');
        removeColons = replaceCommas.replaceAll(";", '')
        console.log(removeBrackets);
        console.log(string);
        console.log(replaceCommas);
        console.log(removeColons);
        arrayContainers[i].textContent = removeColons;
    }
};

function makeUL(array) {
    // Create the list element:
    let list = document.createElement('ul');

    for (let i = 0; i < array.length; i++) {
        // Create the list item:
        let item = document.createElement('li');

        // Set its contents:
        item.appendChild(document.createTextNode(array[i]));

        // Add it to the list:
        list.appendChild(item);
    }

    // Finally, return the constructed list:
    return list;
}

function makeOL(array) {
    // Create the list element:
    let list = document.createElement('ol');

    for (let i = 0; i < array.length; i++) {
        // Create the list item:
        let item = document.createElement('li');

        // Set its contents:
        item.appendChild(document.createTextNode(array[i]));

        // Add it to the list:
        list.appendChild(item);
    }

    // Finally, return the constructed list:
    return list;
}

function turnStringIntoArray() {
    let stringContainers = document.getElementsByClassName("string-to-array")
    let string;
    let removeBrackets;
    let removeQuotes;
    let array;
    for(let i=0; i<stringContainers.length; i++) {
        string = stringContainers[i].textContent;
        console.log(string)
        removeBrackets = string.replace(/\[|\]/g, '');
        removeQuotes = removeBrackets.replace(/['"]+/g, '')
        array = removeQuotes.split(", ");
        // Add the contents
        stringContainers[i].textContent = ""
        stringContainers[i].appendChild(makeUL(array));
    }
};

function turnStepsStringIntoArray() {
    let stringContainers = document.getElementsByClassName("steps-string-to-array")
    let string;
    let removeBrackets;
    let removeQuotes;
    let array;
    for(let i=0; i<stringContainers.length; i++) {
        string = stringContainers[i].textContent;
        console.log(string)
        removeBrackets = string.replace(/\[|\]/g, '');
        console.log(removeBrackets);
        removeQuotes = removeBrackets.slice(1, -1)
        console.log(removeQuotes);
        array = removeQuotes.split("', '");
        // Add the contents
        stringContainers[i].textContent = ""
        stringContainers[i].appendChild(makeOL(array));
    }
};

function colourSwatch() {
    let selected = document.getElementsByClassName("selected");
    if(selected.length > 0){
        let colour = selected[2];
        let colourCode = selected[2].textContent;
        let colourTextNode = colour.children[0];
        console.log(colourCode);
        console.log(colourTextNode);
        let newSwatch = document.createElement("span");
        newSwatch.id = ("swatch");
        newSwatch.style.backgroundColor = colourCode;
        newSwatch.textContent = `Currently Selected: ${colourCode}`;
        colour.removeChild(colourTextNode);
        colour.appendChild(newSwatch);
    }
};

$(document).ready(function(){
    $('.sidenav').sidenav();
    $('select').formSelect();
    $('.tooltipped').tooltip();
    $('.modal').modal();

    validateMaterializeSelect();
    function validateMaterializeSelect() {
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }

    setRecipeColourImage();
    turnArrayIntoString();
    turnStringIntoArray();
    turnStepsArrayIntoString();
    turnStepsStringIntoArray();
    colourSwatch();

    $('#ingrediant_list').keypress(function (e) {
        if (e.which == 13) {
            e.preventDefault();
            console.log("button pressed")
        }
    });
});
