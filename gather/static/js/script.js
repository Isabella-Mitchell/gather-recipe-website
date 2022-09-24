 //Functions


/**
 * Sets the background colour of the recipe card image based on the recipe's colour code 
 * */
 function setRecipeImage() {
    let recipeImages = document.getElementsByClassName("image-url");
    let parent
    let imageUrl
    for(let i = 0; i < recipeImages.length; i++) {
        parent = recipeImages[i].parentNode;
        imageUrl = recipeImages[i].textContent;
        if (imageUrl != ""){
            parent.style.backgroundImage = "url(" + imageUrl + ")";
            parent.style.backgroundRepeat = "no-repeat";
            parent.style.backgroundSize = "cover";
            parent.style.backgroundPosition = "center";
        } else {
            parent.classList.add("holding-image")
        }
    }
};

/**
 * Used in Edit Recipe form. Takes data stored as an array in MongoDB and presents it as a string.
 * Uses , to seperate list items
 * TO DO - Refactor array/ string functions. Or change to use JSON
 * */
function turnArrayIntoString() {
    let arrayContainers = document.getElementsByClassName("array-string");
    let array;
    let removeBrackets;
    let string;
    for(let i = 0; i < arrayContainers.length; i++) {
        array = arrayContainers[i].textContent;  
        removeBrackets = array.replace(/\[|\]/g, '');
        string = removeBrackets.replace(/['"]+/g, '')
        arrayContainers[i].textContent = string
    }
};

/**
 * Used in Edit Recipe form. Takes instructions data stored as an array in MongoDB and presents it as a string.
 * Uses \r\n to seperate steps
 * TO DO - Refactor array/ string functions. Or change to use JSON
 * */
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
        arrayContainers[i].textContent = removeColons;
    }
};


/**
 * Makes an Ul out of array passed into the function
 * returns the list
 * */
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

/**
 * Makes an Ol out of array passed into the function
 * returns the list
 * */
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


/**
 * Used on Find Recipes, Dashboard and View Recipes. 
 * Takes data stored as an array in MongoDB, removes formatting and turns it into an JS array.
 * Uses , to seperate list items
 * Calls makeUL function to show array as an unordered list
 * TO DO - Refactor array/ string functions. Or change to use JSON
 * */
function turnStringIntoArray() {
    let stringContainers = document.getElementsByClassName("string-to-array")
    let string;
    let removeBrackets;
    let removeQuotes;
    let array;
    for(let i=0; i<stringContainers.length; i++) {
        string = stringContainers[i].textContent;
        removeBrackets = string.replace(/\[|\]/g, '');
        removeQuotes = removeBrackets.replace(/['"]+/g, '')
        array = removeQuotes.split(", ");
        // Add the contents
        stringContainers[i].textContent = ""
        stringContainers[i].appendChild(makeUL(array));
    }
};

/**
 * Used on Find Recipes, Dashboard and View Recipes. 
 * Takes data stored as an array in MongoDB, removes formatting and turns it into an JS array.
 * Uses ', ' to seperate steps
 * Calls makeOIL function to show array as an ordered list
 * TO DO - Refactor array/ string functions. Or change to use JSON
 * */
function turnStepsStringIntoArray() {
    let stringContainers = document.getElementsByClassName("steps-string-to-array")
    let string;
    let removeBrackets;
    let removeQuotes;
    let array;
    for(let i=0; i<stringContainers.length; i++) {
        string = stringContainers[i].textContent;
        removeBrackets = string.replace(/\[|\]/g, '');
        // removes outer quotes that still appear
        removeQuotes = removeBrackets.slice(1, -1)
        array = removeQuotes.split("', '");
        // Add the contents
        stringContainers[i].textContent = ""
        stringContainers[i].appendChild(makeOL(array));
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

    turnArrayIntoString();
    turnStringIntoArray();
    turnStepsArrayIntoString();
    turnStepsStringIntoArray();
    setRecipeImage();

    //To stop people entering instead of using commas.
    $('#ingrediant_list').keypress(function (e) {
        if (e.which == 13) {
            e.preventDefault();
        }
    });
});
