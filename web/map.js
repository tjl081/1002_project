
$(document).ready(function () {
    let getrecordId = new URLSearchParams(window.location.search);
    if (getrecordId.has('recordId')) {
        recordId = getrecordId.get('recordId');
        console.log(recordId);
        eel.getColumns(recordId)(displayColumn);;
        displayRow(recordId)
        //eel.getRow(recordId)(displayRow);
        // eel.getplaces()

    }
    else {
        console.log("error retrieving recordId");
    }

});
async function displayColumn(header_list) {
    //header_list = await eel.getColumns(getrecordId)();
    console.log(header_list);
    for (let index = 0; index < header_list.length; index++) {
        $("#main-table thead tr").append(`<th>${header_list[index]}</th>`);
    }
}

//display data in table
//display map after
block = ""
street = ""
async function displayRow(getrecordId) {
    //header_list = await eel.getColumns(getrecordId)();
    record_list = await eel.getRow(getrecordId)();
    console.log(record_list);
    block = "";
    for (let index = 1; index < record_list.length; index++) {
        $("#main-table tbody").append(`<td id="${index}">${record_list[index]}</td>`);
    }
    block = record_list[4];
    street = record_list[5];
    console.log("block in displayRow is " + block + ", street is " + street);
    //viewFlex(street, block);
    postalcode = await eel.getPostalCode(street, block)();
    console.log(postalcode);
    viewMap(postalcode);
    console.log("eel.getPostalCode completed");
    category = "";
    // $("#categories").on("input", function () {
    //     category = $(this).val();
    //     console.log("category is: " + category);
    //     category = category.toLowerCase();
    //     console.log(category);
    //     if (category == 'public transport') {
    //         category = 'public_transport'
    //     }
    //     console.log(category);
    //     //run code
    // });
    category = "";
    const select = document.getElementById('categories');

    select.addEventListener('change', async function handleChange() {
        category = select.options[select.selectedIndex].text;
        category = category.toLowerCase();
        places = await eel.getplaces(postalcode, category)();
        console.log(places);
        viewAmenities(places);

    });

    //console.log(category);
    //places = await eel.getplaces(postalcode, category)();
    //viewAmenities(places);
    // eel.getplaces(eel.getPostalCode(street, block), category);
}


function viewMap(postalcode) {
    url = "https://developers.onemap.sg/commonapi/staticmap/getStaticImage?layerchosen=default&postal=" + postalcode + "&zoom=17&height=512&width=512";
    document.getElementById('imagestore').innerHTML = "<img src='" + url + "' />";

}

function viewAmenities(input_dict) {
    console.log(input_dict);
    for (i = 0; i < input_dict.length; i++) {
        row_value_str = ""
        console.log(input_dict[i])
        for (var val of Object.values(input_dict[i])) {
            console.log(val)
            // console.log(input_dict[val])
            row_value_str += `<td>${val}</td>`
        }
        $("#facil-table tbody").append(`<tr>${row_value_str}</tr>`)


        // console.log(input_dict[i]["name"]);
        // $("#facil-table tbody").append(`<tr><td>${input_dict[i]["name"]}</td></tr>`)

        // $("#facil-table tbody").append(`<tr><td>${input_dict[i]["amenity"]}</td></tr>`)
        // $("#facil-table tbody").append(`<tr><td>${input_dict[i]["distance"]}</td></tr>`)
        // $("#facil-table tbody").append(`<tr><td>${input_dict[i]["postcode"]}</td></tr>`)

    }



    // $("#facil-table tbody").append(`<tr>${}</tr>`)
}


